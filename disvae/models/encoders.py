"""
Module containing the encoders.
"""
import numpy as np

import torch
from torch import nn


# ALL encoders should be called Enccoder<Model>
def get_encoder(model_type):
    model_type = model_type.lower().capitalize()
    return eval("Encoder{}".format(model_type))


class EncoderBurgess(nn.Module):
    def __init__(self, img_size,
                 latent_dim=10):
        r"""Encoder of the model proposed in [1].

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 4 convolutional layers (each with 32 channels), (4 x 4 kernel), (stride of 2)
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
            - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)
0
        References:
            [1] Burgess, Christopher P., et al. "Understanding disentangling in
            $\beta$-VAE." arXiv preprint arXiv:1804.03599 (2018).
        """
        super(EncoderBurgess, self).__init__()

        # Layer parameters
        hid_channels = 32
        kernel_size = 4
        hidden_dim = 256
        self.latent_dim = latent_dim
        self.img_size = img_size
        # Shape required to start transpose convs
        self.reshape = (hid_channels, kernel_size, kernel_size)
        n_chan = self.img_size[0]

        # Convolutional layers
        cnn_kwargs = dict(stride=2, padding=1)
        self.conv1 = nn.Conv2d(n_chan, hid_channels, kernel_size, **cnn_kwargs)
        self.conv2 = nn.Conv2d(hid_channels, hid_channels, kernel_size, **cnn_kwargs)
        self.conv3 = nn.Conv2d(hid_channels, hid_channels, kernel_size, **cnn_kwargs)

        # If input image is 64x64 do fourth convolution
        if self.img_size[1] == self.img_size[2] == 64:
            self.conv_64 = nn.Conv2d(hid_channels, hid_channels, kernel_size, **cnn_kwargs)

        # Fully connected layers
        self.lin1 = nn.Linear(np.prod(self.reshape), hidden_dim)
        self.lin2 = nn.Linear(hidden_dim, hidden_dim)

        # Fully connected layers for mean and variance
        self.mu_logvar_gen = nn.Linear(hidden_dim, self.latent_dim * 2)

    def forward(self, x):
        batch_size = x.size(0)

        # Convolutional layers with ReLu activations
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        if self.img_size[1] == self.img_size[2] == 64:
            x = torch.relu(self.conv_64(x))

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))
        x = torch.relu(self.lin2(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar



class EncoderFullyconnected1(nn.Module):
    """ Fully connected encoder 1

         self.latent_dim = latent_dim
        self.img_size = img_size

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
        - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)

   """
    
    def __init__(self, img_size, latent_dim=128):

        super(EncoderFullyconnected1, self).__init__()

        self.latent_dim = latent_dim
        self.img_size = img_size
        
        dims = [128, 64, 32]
        
        self.lin1 = nn.Linear(np.prod(img_size), dims[0])
        self.lin2 = nn.Linear(dims[0], dims[1])
        self.lin3 = nn.Linear(dims[1], dims[2])
        self.mu_logvar_gen = nn.Linear(dims[2], self.latent_dim * 2)


    def forward(self, x):
        batch_size = x.size(0)

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))
        x = torch.relu(self.lin2(x))
        x = torch.relu(self.lin3(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar



    
class EncoderFullyconnected2(nn.Module):
    """ Fully connected encoder 2

         self.latent_dim = latent_dim
        self.img_size = img_size

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
        - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)

   """
    
    def __init__(self, img_size, latent_dim=128):

        super(EncoderFullyconnected2, self).__init__()

        self.latent_dim = latent_dim
        self.img_size = img_size
        
        dims = [4096, 1024]
        
        self.lin1 = nn.Linear(np.prod(img_size), dims[0])
        self.lin2 = nn.Linear(dims[0], dims[1])
        self.mu_logvar_gen = nn.Linear(dims[1], self.latent_dim * 2)


    def forward(self, x):
        batch_size = x.size(0)

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))
        x = torch.relu(self.lin2(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar


class EncoderFullyconnected3(nn.Module):
    """ Fully connected encoder 3

         self.latent_dim = latent_dim
        self.img_size = img_size

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
        - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)

   """
    
    def __init__(self, img_size, latent_dim=128):

        super(EncoderFullyconnected3, self).__init__()

        self.latent_dim = latent_dim
        self.img_size = img_size
        
        dims = [1024, 1024]
        
        self.lin1 = nn.Linear(np.prod(img_size), dims[0])
        self.lin2 = nn.Linear(dims[0], dims[1])
        self.mu_logvar_gen = nn.Linear(dims[1], self.latent_dim * 2)


    def forward(self, x):
        batch_size = x.size(0)

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))
        x = torch.relu(self.lin2(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar


class EncoderFullyconnected4(nn.Module):
    """ Fully connected encoder 4

         self.latent_dim = latent_dim
        self.img_size = img_size

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
        - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)

   """
    
    def __init__(self, img_size, latent_dim=128):

        super(EncoderFullyconnected4, self).__init__()

        self.latent_dim = latent_dim
        self.img_size = img_size
        
        dims = [128, 32]
        
        self.lin1 = nn.Linear(np.prod(img_size), dims[0])
        self.lin2 = nn.Linear(dims[0], dims[1])
        self.mu_logvar_gen = nn.Linear(dims[1], self.latent_dim * 2)


    def forward(self, x):
        batch_size = x.size(0)

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))
        x = torch.relu(self.lin2(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar


    
class EncoderFullyconnected5(nn.Module):
    """ Fully connected encoder 5

         self.latent_dim = latent_dim
        self.img_size = img_size

        Parameters
        ----------
        img_size : tuple of ints
            Size of images. E.g. (1, 32, 32) or (3, 64, 64).

        latent_dim : int
            Dimensionality of latent output.

        Model Architecture (transposed for decoder)
        ------------
        - 2 fully connected layers (each of 256 units)
        - Latent distribution:
        - 1 fully connected layer of 20 units (log variance and mean for 10 Gaussians)

   """
    
    def __init__(self, img_size, latent_dim=128, dropout_p = 0.2):

        super(EncoderFullyconnected5, self).__init__()

        self.latent_dim = latent_dim
        self.img_size = img_size
        
        dims = [128]
        
        self.lin1 = nn.Linear(np.prod(img_size), dims[0])
        self.dropout = nn.Dropout(dropout_p)
        self.mu_logvar_gen = nn.Linear(dims[0], self.latent_dim * 2)


    def forward(self, x):
        batch_size = x.size(0)

        # Fully connected layers with ReLu activations
        x = x.view((batch_size, -1))
        x = torch.relu(self.lin1(x))

        # Fully connected layer for log variance and mean
        # Log std-dev in paper (bear in mind)
        mu_logvar = self.mu_logvar_gen(x)
        mu, logvar = mu_logvar.view(-1, self.latent_dim, 2).unbind(-1)

        return mu, logvar
