# Changes

Most recent releases are shown at the top. Each release shows:

- **New**: New classes, methods, functions, etc
- **Changed**: Additional parameters, changes to inputs or outputs, etc
- **Fixed**: Bug fixes that don't change documented behaviour

## 0.2.5 (2019-08-27)

### New:
- ```explain``` methods have been added to ```TextPredictor``` and ```ImagePredictor``` objects.
- ```TextPredictor.predict_proba``` and ```ImagePredictor.predict_proba_*``` convenience
methods have been added.
- Added ```utils.is_classifier``` utility function

### Changed:
- ```TextPredictor.predict``` method can now accept a single document as input instead of
always requiring a list.
- Output of ```core.view_top_losses``` now includes the ground truth label of examples

### Fixed:
- Fixed test of data loading


## 0.2.4 (2019-08-20)

### New:
- added additional tests of *ktrain*

### Changed:
- Added ```classes``` argument to ```vision.images_from_folder```.  Only classes/subfolders
  matching a name in the ```classes``` list will be considered.

### Fixed:
- Resolved issue with using ```learner.view_top_losses``` with BERT models.


## 0.2.3 (2019-08-18)

### New:
- N/A

### Changed:
- Added ```classes``` argument to ```vision.images_from_folder```.  Only classes/subfolders
  matching a name in the ```classes``` list will be considered.

### Fixed:
- Fixed issue with ```learner.validate``` and ```learner.predict``` failing when validation data is in 
  the form of an Iterator (e.g., DirectoryIterator).


## 0.2.2 (2019-08-16)

### New:
- N/A

### Changed:
- Added check in ```ktrain.lroptimize.lrfinder``` to stop training if learning rate exceeds a fixed maximum,
  which may happen when bad/dysfunctional model is supplied to learning rate finder.

### Fixed:
- In ```ktrain.text.data.texts_from_folder``` function, only subfolders specified in classes argument 
  are read in as training and validation data.

## 0.2.1 (2019-08-15)

### New:
- N/A

### Changed:
- N/A

### Fixed:
- Fixed error related to validation_steps=None in call to fit_generator in ```ktrain.core``` on Google Colab.


## 0.2.0 (2019-08-12)

### New:
- Support for pretrained BERT Text Classification 

### Changed:
- For ```Learner.lr_find```, added optional ```max_epochs``` argument. 
- Changed ```Learner.confusion_matrix``` to ```Learner.validate``` and added optional ```val_data``` argument.
  The ```use_valid``` argument has been removed.
- Removed ```pretrained_fpath``` argument to ```text.text_classifier```.  Pretrained word vectors are
  now downloaded automatically when 'bigru' is selected as model.

### Fixed:
- Further cleanup of  ```utils.is_iter``` function to use type check.





## 0.1.10 (2019-08-02)

### New:
- N/A

### Changed:
- For ```Learner.lr_find```, removed epochs and max_lr arguments and added lr_mult argument
  Default lr_mult is 1.01, but can be changed to control size of sample being used
  to estimate learning rate.
- Changed structure of examples folder

### Fixed:
- Resolved issue with ```utils.y_from_data``` not working correctly with DataFrameIterator objects.


## 0.1.9 (2019-08-01)

### New:
- N/A

### Changed:
- Use class check in utils.is_iter as temporary fix
- revert to epochs=5 for ```Learner.lr_find```

### Fixed:
- N/A

## 0.1.8 (2019-06-04)

### New:
- N/A

### Changed:
- N/A

### Fixed:
- ```Learner.set_weight_decay``` now works correctly


## 0.1.7 (2019-05-24)

### New:
- BIGRU text classifier: Bidirectional GRU using pretrained word embeddings

### Changed:
- Epochs are calculated automatically in ```LRFinder```

### Fixed:
- Number of epochs that ```Learner.lr_find``` runs can be explicitly set again


## 0.1.6 (2019-05-03)

### New:

### Changed:
- relocated calls to tensorflow 
- installation instructions and reformatted examples

### Fixed:



## 0.1.5 (2019-05-01)

### New:
- **cycle\_momentum** argument for both```autofit``` and ```fit_onecycle``` method that will cycle momentum between 0.95 and 0.85 as described in [this paper](https://arxiv.org/abs/1803.09820)
- ```Learner.plot``` method that will plot training-validation loss, LR schedule, or momentum schedule
- added ```set_weight_decay``` and ```get_weight_decay``` methods to get/set "global" weight decay in Keras

### Changed:
- ```vision.data.preview_data_aug``` now displays images in rows by default
- added multigpu flag to ```core.get_learner``` with comment that it is only supported by```vision.model.image_classifier```
- added ```he_normal``` initialization to FastText model

### Fixed:

- Bug in ```vision.data.images_from_fname``` that prevented relative paths for directory argument
- Bug in ```utils.y_from_data``` that returned incorrect information for array-based training/validation data
- Bug in ```core.autofit``` with callback failure when validation data is not set
- Bug in ```core.autofit``` and ```core.fit_onecycle``` with learning rate setting at end of cycle


## 0.1.4 (2019-04-10)

- Last release without CHANGELOG updates



