import os
import re
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any
from .textgen import CopyWriter


class ContentRecommender:
    def __init__(self, csv_path: str, index_dir: str, model_name: str):
        self.csv_path = csv_path
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)

        self.df = pd.read_csv(csv_path)

        # -----------------------
        # Preprocessing
        # -----------------------

        # 1) Fill missing text fields
        for col in ["title", "brand", "description", "categories", "material", "color"]:
            if col not in self.df.columns:
                self.df[col] = ""
            self.df[col] = self.df[col].fillna("")

        # 2) Clean price column -> USD float, fill NaN with median
        if "price" in self.df.columns:
            # Keep only digits and decimal point, e.g. "$1,149.99" -> "1149.99"
            self.df["price"] = (
                self.df["price"].astype(str).str.replace(r"[^\d\.]", "", regex=True)
            )
            self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
            if self.df["price"].notna().any():
                median_price = float(self.df["price"].median())
                self.df["price"] = self.df["price"].fillna(median_price)
            else:
                # If everything is NaN, set to 0.0 to keep analytics working
                self.df["price"] = 0.0

        # 3) Build text field for embeddings
        self.df["text"] = (
            self.df["title"]
            + " "
            + self.df["brand"]
            + " "
            + self.df["categories"]
            + " "
            + self.df["material"]
            + " "
            + self.df["color"]
            + " "
            + self.df["description"]
        )

        # Embeddings
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.index = None
        self.copy = CopyWriter()
        self._ensure_index()

    # ---------- helpers ----------
    def _clean_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Make values JSON-safe: convert NaN/inf -> None; numpy types -> py types."""
        import math

        cleaned = {}
        for k, v in d.items():
            if v is None:
                cleaned[k] = None
            elif isinstance(v, (np.floating, float)):
                if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) or (
                    isinstance(v, np.floating) and (np.isnan(v) or np.isinf(v))
                ):
                    cleaned[k] = None
                else:
                    cleaned[k] = float(v)
            elif isinstance(v, (np.integer,)):
                cleaned[k] = int(v)
            else:
                cleaned[k] = v if v == v else None  # catch NaN
        return cleaned

    def _json_safe(self, obj):
        """Recursively sanitize dict/list values for JSON."""
        import math

        if isinstance(obj, dict):
            return {k: self._json_safe(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._json_safe(x) for x in obj]
        if isinstance(obj, (np.floating, float)):
            try:
                f = float(obj)
            except Exception:
                return None
            return None if (np.isnan(f) or np.isinf(f) or math.isnan(f)) else f
        if isinstance(obj, (np.integer,)):
            return int(obj)
        return obj

    def _first_image_url(self, images_val) -> str:
        """Return a single usable image URL from the dataset value."""
        if not isinstance(images_val, str):
            return ""
        s = images_val.strip()

        # Case A: pipe-delimited: "url1|url2|..."
        if "|" in s:
            first = s.split("|")[0].strip()
            if first.startswith("http"):
                return first

        # Case B: looks like a Python-list-as-string: "['url1', ' url2', ...]"
        m = re.search(r"https?://[^\s'\",]+", s)
        return m.group(0) if m else ""

    def _ensure_index(self):
        idx_path = os.path.join(self.index_dir, "faiss.index")
        npy_path = os.path.join(self.index_dir, "embeddings.npy")
        if os.path.exists(idx_path) and os.path.exists(npy_path):
            self.embeddings = np.load(npy_path)
            self.index = faiss.read_index(idx_path)
            return

        # Build embeddings
        texts = self.df["text"].tolist()
        self.embeddings = np.array(
            self.model.encode(texts, show_progress_bar=True), dtype="float32"
        )

        # cosine similarity via L2-normalized inner product
        faiss.normalize_L2(self.embeddings)
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

        np.save(npy_path, self.embeddings)
        faiss.write_index(self.index, idx_path)

    # ---------- API used methods ----------
    def recommend(self, prompt: str, top_k: int = 6, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Encode prompt
        vec = self.model.encode([prompt]).astype("float32")
        faiss.normalize_L2(vec)

        scores, idxs = self.index.search(vec, top_k * 3)  # overfetch before filtering
        results: List[Dict[str, Any]] = []

        for i, s in zip(idxs[0], scores[0]):
            row = self.df.iloc[int(i)].to_dict()

            # Optional keyword filters (case-insensitive "contains")
            if filters:
                ok = True
                for k, v in filters.items():
                    if k in row and str(v).lower() not in str(row[k]).lower():
                        ok = False
                        break
                if not ok:
                    continue

            # Creative blurb + sanitize + normalize image URL
            row["gen_description"] = self.copy.generate(
                row.get("title", ""), row.get("description", ""), row.get("categories", "")
            )
            row["score"] = float(s)
            row = self._clean_dict(row)
            row["images"] = self._first_image_url(row.get("images", ""))

            results.append(row)
            if len(results) >= top_k:
                break

        return results

    def item(self, uniq_id: str) -> Dict[str, Any]:
        row = self.df[self.df["uniq_id"] == uniq_id]
        if row.empty:
            return {}
        r = row.iloc[0].to_dict()
        r["gen_description"] = self.copy.generate(
            r.get("title", ""), r.get("description", ""), r.get("categories", "")
        )
        r = self._clean_dict(r)
        r["images"] = self._first_image_url(r.get("images", ""))
        return r

    def analytics(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if "brand" in self.df.columns:
            out["top_brands"] = self.df["brand"].value_counts().head(10).to_dict()

        if "categories" in self.df.columns and "price" in self.df.columns:
            tmp = self.df[["categories", "price"]].copy()
            # price is already numeric & filled; groupby works directly
            if not tmp.empty:
                out["avg_price_by_category"] = (
                    tmp.groupby("categories")["price"]
                    .mean()
                    .sort_values(ascending=False)
                    .head(15)
                    .round(2)
                    .to_dict()
                )

        out["missingness"] = self.df.isna().sum().to_dict()

        if "price" in self.df.columns:
            ps = self.df["price"].describe().round(2).to_dict()
            out["price_summary"] = ps

        # Ensure everything is JSON-safe
        return self._json_safe(out)
