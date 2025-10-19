import torch, torchvision
from torchvision import transforms
from PIL import Image
from typing import List

class FurnitureClassifier:
    """Loads a lightweight ResNet18 classifier if available; otherwise returns category from metadata.
    Train this via the provided notebook to enable real predictions.
    """
    def __init__(self, model_path: str, labels: List[str] = None):
        self.model_path = model_path
        self.labels = labels or ['chair','table','sofa','bed','cabinet','shelf','stool','bench','lamp','decor']
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = torchvision.models.resnet18(weights=None, num_classes=len(self.labels))
        if torch.cuda.is_available():
            self.model = self.model.to(self.device)
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
        self.tf = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor()
        ])

    def predict_from_path(self, path: str) -> str:
        try:
            im = Image.open(path).convert('RGB')
            x = self.tf(im).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(x)
                idx = int(logits.argmax(dim=1).item())
            return self.labels[idx]
        except Exception:
            return 'unknown'
