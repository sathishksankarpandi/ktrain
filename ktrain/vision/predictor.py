from ..imports import *
from ..predictor import Predictor
from .preprocessor import ImagePreprocessor
from .. import utils as U



class ImagePredictor(Predictor):
    """
    predicts image classes
    """

    def __init__(self, model, preproc):

        if not isinstance(model, Model):
            raise ValueError('model must be of instance Model')
        if not isinstance(preproc, ImagePreprocessor):
            raise ValueError('preproc must be instance of ImagePreprocessor')
        self.model = model
        self.preproc = preproc
        self.datagen = self.preproc.get_preprocessor()
        self.c = self.preproc.get_classes()


    def get_classes(self):
        return self.c


    def explain(self, img_fpath):
        """
        Highlights image to explain prediction
        """
        img = image.load_img(img_fpath, 
                             target_size=self.preproc.target_size, 
                             color_mode=self.preproc.color_mode)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        return eli5.show_prediction(self.model, x)




    def predict(self, data, return_proba=False):
        """
        Predicts class from image in array format.
        If return_proba is True, returns probabilities of each class.
        """
        if not isinstance(data, np.ndarray):
            raise ValueError('data must be numpy.ndarray')
        (generator, steps) = self.preproc.preprocess(data)
        return self.predict_generator(generator, steps=steps, return_proba=return_proba)


    def predict_filename(self, img_path, return_proba=False):
        """
        Predicts class from filepath to single image file.
        If return_proba is True, returns probabilities of each class.
        """
        if not os.path.isfile(img_path): raise ValueError('img_path must be valid file')
        (generator, steps) = self.preproc.preprocess(img_path)
        return self.predict_generator(generator, steps=steps, return_proba=return_proba)


    def predict_folder(self, folder, return_proba=False):
        """
        Predicts the classes of all images in a folder.
        If return_proba is True, returns probabilities of each class.
        
        """
        if not os.path.isdir(folder): raise ValueError('folder must be valid directory')
        (generator, steps) = self.preproc.preprocess(folder)
        result = self.predict_generator(generator, steps=steps, return_proba=return_proba)
        if len(result) != len(generator.filenames): 
            raise Exception('number of results does not equal number of filenames')
        return list(zip(generator.filenames, result))


    def predict_generator(self, generator, steps=None, return_proba=False):
        #loss = self.model.loss
        #if callable(loss): loss = loss.__name__
        #treat_multilabel = False
        #if loss != 'categorical_crossentropy' and not return_proba:
        #    return_proba=True
        #    treat_multilabel = True
        classification, multilabel = U.is_classifier(self.model)
        if multilabel: return_proba=True
        preds =  self.model.predict_generator(generator, steps=steps)
        result =  preds if return_proba else [self.c[np.argmax(pred)] for pred in preds] 
        if multilabel:
            return [list(zip(self.c, r)) for r in result]
        else:
            return result


    def predict_proba(self, data):
        return self.predict(data, return_proba=True)


    def predict_proba_folder(self, folder):
        return self.predict_folder(folder, return_proba=True)


    def predict_proba_filename(self, img_path):
        return self.predict_filename(img_path, return_proba=True)


    def predict_proba_generator(self, generator, steps=None):
        return self.predict_proba_generator(generator, steps=steps, return_proba=True)



    def analyze_valid(self, generator, print_report=True, multilabel=None):
        """
        Makes predictions on validation set and returns the confusion matrix.
        Accepts as input a genrator (e.g., DirectoryIterator, DataframeIterator)
        representing the validation set.


        Optionally prints a classification report.
        Currently, this method is only supported for binary and multiclass 
        problems, not multilabel classification problems.

        """
        if multilabel is None:
            multilabel = U.is_multilabel(generator)
        if multilabel:
            warnings.warn('multilabel_confusion_matrix not yet supported - skipping')
            return

        y_true = generator.classes
        y_pred = self.model.predict_generator(generator)
        y_pred = np.argmax(y_pred, axis=1)
        if print_report:
            print(classification_report(y_true, y_pred, target_names=self.c))
        if not multilabel:
            cm_func = confusion_matrix
            cm =  cm_func(y_true,  y_pred)
        else:
            cm = None
        return cm



    def save(self, fname):
        self.model.save(fname)
        fname_preproc = fname+'.preproc'
        with open(fname_preproc, 'wb') as f:
            datagen = self.preproc.get_preprocessor()
            pfunc = datagen.preprocessing_function
            datagen.preprocessing_function = None
            pickle.dump(self.preproc, f)
            datagen.preprocessing_function = pfunc
        return
        
