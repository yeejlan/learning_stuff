import torch
import torchvision
import torchmetrics as tm
from torch.utils.data import DataLoader

n_epochs = 3
batch_size_train = 64
batch_size_test = 1000
learning_rate = 0.01
momentum = 0.5
log_interval = 10
random_seed = 1
torch.manual_seed(random_seed)

train_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('./data/', train=True, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor(),
                               torchvision.transforms.Normalize(
                                 (0.1307,), (0.3081,))
                             ])),
  batch_size=batch_size_train, shuffle=True)
test_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('./data/', train=False, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor(),
                               torchvision.transforms.Normalize(
                                 (0.1307,), (0.3081,))
                             ])),
  batch_size=batch_size_test, shuffle=False)

examples = enumerate(test_loader)
batch_idx, (example_data, example_targets) = next(examples)
# print(example_targets)
# print(example_targets.shape)
# print(example_data.shape)

import matplotlib.pyplot as plt
# plt.figure()
# for i in range(6):
#   plt.subplot(2,3,i+1)
#   plt.tight_layout()
#   plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
#   plt.title("Ground Truth: {}".format(example_targets[i]))
#   plt.xticks([])
#   plt.yticks([])
# plt.show()

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, kernel_size=5)
        self.conv2 = nn.Conv2d(20, 40, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(640, 128)
        self.fc2 = nn.Linear(128, 10)
    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 640)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

import pytorch_lightning as pl
from pytorch_lightning import Trainer
from pytorch_lightning.core.lightning import LightningModule

class LitNet(Net, LightningModule):
    def __init__(self):
        super().__init__()  
        self.train_acc = tm.Accuracy()
        self.test_acc = tm.Accuracy()        
    
    def training_step(self, batch, batch_idx):
        data, target = batch
        logits = self.forward(data)
        loss = F.nll_loss(logits, target)
        self.log('train_loss', loss)
        self.log('train_acc', self.train_acc(logits, target), on_step=True, on_epoch=False)
        return {'loss': loss}
    
    def configure_optimizers(self):
        return optim.SGD(self.parameters(), lr=learning_rate,
                      momentum=momentum) 

    def test_step(self, batch, batch_idx):
        data, target = batch
        logits = self.forward(data)
        loss = F.nll_loss(logits, target)
        self.log('test_loss', loss)
        self.log('test_acc', self.test_acc(logits, target), on_step=False, on_epoch=True)


from pytorch_lightning import loggers as pl_loggers

model = LitNet()
trainer = Trainer(max_epochs=15, gpus=1)
trainer.fit(model, train_loader)
trainer.test(model, test_dataloaders=test_loader)