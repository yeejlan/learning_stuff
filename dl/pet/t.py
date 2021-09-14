import torch

def nonzero_tuple(x):
    """
    A 'as_tuple=True' version of torch.nonzero to support torchscript.
    because of https://github.com/pytorch/pytorch/issues/38718
    """
    if torch.jit.is_scripting():
        if x.dim() == 0:
            return x.unsqueeze(0).nonzero().unbind(1)
        return x.nonzero().unbind(1)
    else:
        return x.nonzero(as_tuple=True)

gt_classes = torch.tensor([-1, 0, 1,2,3,4,5])
num_classes = 3

c = gt_classes >= 0
d = gt_classes < num_classes
e = c & d

print(c)
print(d)
print(e)
print(nonzero_tuple(e)[0])