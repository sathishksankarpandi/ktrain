#!/usr/bin/env python3
"""
Tests of ktrain text classification flows
"""
import sys
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID";
os.environ["CUDA_VISIBLE_DEVICES"]="0"
sys.path.insert(0,'../..')
import IPython
from unittest import TestCase, main, skip
import numpy as np
import ktrain
from ktrain import text as txt
TEST_DOC = 'god christ jesus mother mary church sunday lord heaven amen'

class TestTextClassification(TestCase):

    def setUp(self):
        # fetch the dataset using scikit-learn
        categories = ['alt.atheism', 'soc.religion.christian',
                     'comp.graphics', 'sci.med']
        from sklearn.datasets import fetch_20newsgroups
        train_b = fetch_20newsgroups(subset='train',
           categories=categories, shuffle=True, random_state=42)
        test_b = fetch_20newsgroups(subset='test',
           categories=categories, shuffle=True, random_state=42)
        print('size of training set: %s' % (len(train_b['data'])))
        print('size of validation set: %s' % (len(test_b['data'])))
        print('classes: %s' % (train_b.target_names))
        x_train = train_b.data
        y_train = train_b.target
        x_test = test_b.data
        y_test = test_b.target
        self.trn = (x_train, y_train)
        self.val = (x_test, y_test)
        self.classes = train_b.target_names



    def test_fasttext(self):
        trn, val, preproc = txt.texts_from_array(x_train=self.trn[0], 
                                                 y_train=self.trn[1],
                                                 x_test=self.val[0], 
                                                 y_test=self.val[1],
                                                 class_names=self.classes,
                                                 preprocess_mode='standard',
                                                 maxlen=350, 
                                                 max_features=35000)
        model = txt.text_classifier('fasttext', train_data=trn)
        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)
        lr = 0.01
        hist = learner.fit(lr, 10, cycle_len=1)

        # test training results
        self.assertAlmostEqual(max(hist.history['lr']), lr)
        self.assertGreater(max(hist.history['val_acc']), 0.8)


        # test top losses
        obs = learner.top_losses(n=1, val_data=None)
        self.assertIn(obs[0][0], list(range(len(val[0]))))
        learner.view_top_losses(preproc=preproc, n=1, val_data=None)

        # test weight decay
        self.assertEqual(len(learner.get_weight_decay()), 2)
        self.assertEqual(learner.get_weight_decay()[0], None)
        learner.set_weight_decay(1e-4)
        self.assertAlmostEqual(learner.get_weight_decay()[0], 1e-4)

        # test load and save model
        learner.save_model('/tmp/test_model')
        learner.load_model('/tmp/test_model')

        # test validate
        cm = learner.validate()
        print(cm)
        for i, row in enumerate(cm):
            self.assertEqual(np.argmax(row), i)

        # test predictor
        p = ktrain.get_predictor(learner.model, preproc)
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        p.save('/tmp/test_predictor')
        p = ktrain.load_predictor('/tmp/test_predictor')
        self.assertEqual(p.predict(TEST_DOC), 'soc.religion.christian')
        self.assertEqual(np.argmax(p.predict_proba([TEST_DOC])[0]), 3)
        self.assertEqual(type(p.explain(TEST_DOC)), IPython.core.display.HTML)


    def test_nbsvm(self):
        trn, val, preproc = txt.texts_from_array(x_train=self.trn[0], 
                                                 y_train=self.trn[1],
                                                 x_test=self.val[0], 
                                                 y_test=self.val[1],
                                                 class_names=self.classes,
                                                 preprocess_mode='standard',
                                                 maxlen=700, 
                                                 max_features=35000,
                                                 ngram_range=3)
        model = txt.text_classifier('nbsvm', train_data=trn)
        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)
        lr = 0.01
        hist = learner.fit_onecycle(lr, 10)

        # test training results
        self.assertAlmostEqual(max(hist.history['lr']), lr)
        self.assertGreater(max(hist.history['val_acc']), 0.92)
        self.assertAlmostEqual(max(hist.history['momentum']), 0.95)
        self.assertAlmostEqual(min(hist.history['momentum']), 0.85)


        # test top losses
        obs = learner.top_losses(n=1, val_data=None)
        self.assertIn(obs[0][0], list(range(len(val[0]))))
        learner.view_top_losses(preproc=preproc, n=1, val_data=None)

        # test weight decay
        self.assertEqual(len(learner.get_weight_decay()), 0)
        learner.set_weight_decay(1e-4)
        self.assertEqual(len(learner.get_weight_decay()), 0)

        # test load and save model
        learner.save_model('/tmp/test_model')
        learner.load_model('/tmp/test_model')

        # test validate
        cm = learner.validate()
        print(cm)
        for i, row in enumerate(cm):
            self.assertEqual(np.argmax(row), i)

        # test predictor
        p = ktrain.get_predictor(learner.model, preproc)
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        p.save('/tmp/test_predictor')
        p = ktrain.load_predictor('/tmp/test_predictor')
        self.assertEqual(p.predict(TEST_DOC), 'soc.religion.christian')
        self.assertEqual(np.argmax(p.predict_proba([TEST_DOC])[0]), 3)
        self.assertEqual(type(p.explain(TEST_DOC)), IPython.core.display.HTML)

    def test_logreg(self):
        trn, val, preproc = txt.texts_from_array(x_train=self.trn[0], 
                                                 y_train=self.trn[1],
                                                 x_test=self.val[0], 
                                                 y_test=self.val[1],
                                                 class_names=self.classes,
                                                 preprocess_mode='standard',
                                                 maxlen=700, 
                                                 max_features=35000,
                                                 ngram_range=3)
        model = txt.text_classifier('nbsvm', train_data=trn)
        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)
        lr = 0.01
        hist = learner.autofit(lr)

        # test training results
        self.assertAlmostEqual(max(hist.history['lr']), lr)
        self.assertGreater(max(hist.history['val_acc']), 0.92)
        self.assertAlmostEqual(max(hist.history['momentum']), 0.95)
        self.assertAlmostEqual(min(hist.history['momentum']), 0.85)


        # test top losses
        obs = learner.top_losses(n=1, val_data=None)
        self.assertIn(obs[0][0], list(range(len(val[0]))))
        learner.view_top_losses(preproc=preproc, n=1, val_data=None)

        # test weight decay
        self.assertEqual(len(learner.get_weight_decay()), 0)
        learner.set_weight_decay(1e-4)
        self.assertEqual(len(learner.get_weight_decay()), 0)

        # test load and save model
        learner.save_model('/tmp/test_model')
        learner.load_model('/tmp/test_model')

        # test validate
        cm = learner.validate()
        print(cm)
        for i, row in enumerate(cm):
            self.assertEqual(np.argmax(row), i)

        # test predictor
        p = ktrain.get_predictor(learner.model, preproc)
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        p.save('/tmp/test_predictor')
        p = ktrain.load_predictor('/tmp/test_predictor')
        self.assertEqual(p.predict(TEST_DOC), 'soc.religion.christian')
        self.assertEqual(np.argmax(p.predict_proba([TEST_DOC])[0]), 3)
        self.assertEqual(type(p.explain(TEST_DOC)), IPython.core.display.HTML)


    #@skip('temporarily disabled')
    def test_bigru(self):
        trn, val, preproc = txt.texts_from_array(x_train=self.trn[0], 
                                                 y_train=self.trn[1],
                                                 x_test=self.val[0], 
                                                 y_test=self.val[1],
                                                 class_names=self.classes,
                                                 preprocess_mode='standard',
                                                 maxlen=350, 
                                                 max_features=35000,
                                                 ngram_range=1)
        model = txt.text_classifier('bigru', train_data=trn, preproc=preproc)
        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)
        lr = 0.01
        hist = learner.autofit(lr, 1)

        # test training results
        self.assertAlmostEqual(max(hist.history['lr']), lr)
        self.assertGreater(max(hist.history['val_acc']), 0.9)
        self.assertAlmostEqual(max(hist.history['momentum']), 0.95)
        self.assertAlmostEqual(min(hist.history['momentum']), 0.85)


        # test top losses
        obs = learner.top_losses(n=1, val_data=None)
        self.assertIn(obs[0][0], list(range(len(val[0]))))
        learner.view_top_losses(preproc=preproc, n=1, val_data=None)

        # test weight decay
        self.assertEqual(len(learner.get_weight_decay()), 1)
        self.assertEqual(learner.get_weight_decay()[0], None)
        learner.set_weight_decay(1e-4)
        self.assertAlmostEqual(learner.get_weight_decay()[0], 1e-4)


        # test load and save model
        learner.save_model('/tmp/test_model')
        learner.load_model('/tmp/test_model')

        # test validate
        cm = learner.validate()
        print(cm)
        for i, row in enumerate(cm):
            self.assertEqual(np.argmax(row), i)

        # test predictor
        p = ktrain.get_predictor(learner.model, preproc)
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        p.save('/tmp/test_predictor')
        p = ktrain.load_predictor('/tmp/test_predictor')
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        self.assertEqual(p.predict(TEST_DOC), 'soc.religion.christian')
        self.assertEqual(np.argmax(p.predict_proba([TEST_DOC])[0]), 3)
        self.assertEqual(type(p.explain(TEST_DOC)), IPython.core.display.HTML)


    #@skip('temporarily disabled')
    def test_bert(self):
        trn, val, preproc = txt.texts_from_array(x_train=self.trn[0], 
                                                 y_train=self.trn[1],
                                                 x_test=self.val[0], 
                                                 y_test=self.val[1],
                                                 class_names=self.classes,
                                                 preprocess_mode='bert',
                                                 maxlen=350, 
                                                 max_features=35000)
        model = txt.text_classifier('bert', train_data=trn)
        learner = ktrain.get_learner(model, train_data=trn, batch_size=6)
        lr = 2e-5
        hist = learner.fit_onecycle(lr, 1)

        # test training results
        self.assertAlmostEqual(max(hist.history['lr']), lr)
        self.assertGreater(max(hist.history['acc']), 0.7)


        # test top losses
        obs = learner.top_losses(n=1, val_data=val)
        self.assertIn(obs[0][0], list(range(len(val[0][0]))))
        learner.view_top_losses(preproc=preproc, n=1, val_data=val)

        # test weight decay
        self.assertEqual(len(learner.get_weight_decay()), 2)
        self.assertEqual(learner.get_weight_decay()[0], None)
        learner.set_weight_decay(1e-4)
        self.assertAlmostEqual(learner.get_weight_decay()[0], 1e-4)

        # test load and save model
        learner.save_model('/tmp/test_model')
        learner.load_model('/tmp/test_model')

        # test validate
        cm = learner.validate(val_data=val)
        print(cm)
        for i, row in enumerate(cm):
            self.assertEqual(np.argmax(row), i)

        # test predictor
        p = ktrain.get_predictor(learner.model, preproc)
        self.assertEqual(p.predict([TEST_DOC])[0], 'soc.religion.christian')
        p.save('/tmp/test_predictor')
        p = ktrain.load_predictor('/tmp/test_predictor')
        self.assertEqual(p.predict(TEST_DOC), 'soc.religion.christian')
        self.assertEqual(np.argmax(p.predict_proba([TEST_DOC])[0]), 3)
        self.assertEqual(type(p.explain(TEST_DOC)), IPython.core.display.HTML)




if __name__ == "__main__":
    main()
