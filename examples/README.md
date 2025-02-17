# Example Notebooks

This directory contains various example notebooks using *ktrain*.  The directory currently has two folders:
- **text**:  text classification examples using various models and datasets
- **vision**:  image classification examples using various models and datasets

## Text Classification Datasets

### [IMDb](https://ai.stanford.edu/~amaas/data/sentiment/):  Binary Classification

IMDb is a dataset containing 50K movie reviews labeled as positive or negative.  The corpus is split evenly between training and validation.
The dataset is in the form of folders of images.

- [IMDb-fasttext.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  A simple and fast "custom" fasttext model.
- [IMDb-BERT.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  BERT text classification to predict sentiment of movie reviews.


### [20 News Groups](http://qwone.com/~jason/20Newsgroups/): Multiclass Classification
This is a small sample of the 20newsgroups dataset based on considering 4 newsgroups similar to what was done in the
[Working with Text Data](https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html) scikit-learn tutorial. 
Data are in the form of arrays fetched via scikit-learn library.
These examples show the results of training on a relatively small training set.
- [20newsgroups-NBVSM.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  NBSVM model using unigram features only.
- [20newsgroups-BERT.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  BERT text classification in a multiclass setting.


### [Toxic Comments](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge):  Multi-Label Text Classification
In multi-label classification, a single document can belong to multiple classes.  The objective here is
to categorize each text comment into one or more categories of toxic online behavior.
Dataset is in the form of a CSV file.
- [toxic_comments-fasttext.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  A fasttext-like model applied in a multi-label setting.
- [toxic_comments-bigru.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/text):  A bidirectional GRU using pretrained Glove vectors. This example shows how to use pretreained word vectors using *ktrain*.



## Image Classification Datasets

### [Dogs vs. Cats](https://www.kaggle.com/c/dogs-vs-cats):  Binary Classification
- [dogs_vs_cats-ResNet50.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/vision):  ResNet50 pretrained on ImageNet.  

### [MNIST](http://yann.lecun.com/exdb/mnist/):  Multiclass Classification
- [mnist-WRN22.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/vision):  A randomly-initialized Wide Residual Network applied to MNIST

### [CIFAR10](https://www.cs.toronto.edu/~kriz/cifar.html):  Multiclass Classification
- [cifar10-WRN22.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/vision):  A randomly-initialized Wide Residual Network applied to CIFAR10


### [Pets](https://www.robots.ox.ac.uk/~vgg/data/pets/): Multiclass Classification
- [pets-ResNet50.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/vision):  Categorizing dogs and cats by breed using a pretrained ResNet50. Uses the `images_from_fname` function, as class labels are embedded in the file names of images.


### [Planet](https://www.kaggle.com/c/planet-understanding-the-amazon-from-space): Multilabel Classification
The Kaggle Planet dataset consists of satellite images - each of which are categorized into multiple categories.
Image labels are in the form of a CSV containing paths to images.
- [planet-ResNet50.ipynb](https://github.com/amaiya/ktrain/tree/master/examples/vision):  Using a pretrained ResNet50 model for multi-label classification.



