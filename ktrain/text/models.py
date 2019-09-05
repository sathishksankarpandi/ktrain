from ..imports import *
from .. import utils as U
from . import preprocessor as tpp

NBSVM = 'nbsvm'
FASTTEXT = 'fasttext'
LOGREG = 'logreg'
BIGRU = 'bigru'
BERT = 'bert'
TEXT_CLASSIFIERS = {
                    FASTTEXT: "a fastText-like model (http://arxiv.org/pdf/1607.01759.pdf)",
                    LOGREG:   "logistic regression using a trainable Embedding layer",
                    NBSVM:    "NBSVM model (http://www.aclweb.org/anthology/P12-2018)",
                    BIGRU:    'Bidirectional GRU with pretrained word vectors',
                    BERT:  'Bidirectional Encoder Representations from Transformers (https://arxiv.org/abs/1810.04805)'} 


def print_text_classifiers():
    for k,v in TEXT_CLASSIFIERS.items():
        print("%s: %s" % (k,v))


def calc_pr(y_i, x, y, b):
    idx = np.argwhere((y==y_i)==b)
    ct = x[idx[:,0]].sum(0)+1
    tot = ((y==y_i)==b).sum()+1
    return ct/tot

def calc_r(y_i, x, y):
    return np.log(calc_pr(y_i, x, y, True) / calc_pr(y_i, x, y, False))


def text_classifier(name, train_data, preproc=None, multilabel=None, verbose=1):
    """
    Build and return the default text classification model.

    Args:
        name (string): one of:
                      - 'fasttext' for FastText model
                      - 'nbsvm' for NBSVM model  
                      - 'logreg' for logistic regression
                      - 'bigru' for Bidirectional GRU with pretrained word vectors
                      = 'bert' for BERT Text Classification

        train_data (tuple): a tuple of numpy.ndarrays: (x_train, y_train)
        y_train can either be a list of integers representing classes
        or one-hot-encoded
        preproc: a ktrain.text.TextPreprocessor instance.
                   This is only required for those models
                   that employ pretrained-word vectors (e.g., BIGRU)
        multilabel (bool):  If True, multilabel model will be returned.
                            If false, binary/multiclass model will be returned.
                            If None, multilabel will be inferred from data.
        verbose (boolean): verbosity of output
    Return:
        model (Model): A Keras Model instance
    """
    # check argument
    if not isinstance(train_data, tuple):
        err ="""
            Please pass training data in the form of a tuple of numpy.ndarrays.
            Training set in the form of Iterator is not currently supported
            by get_textmodel
            """
        raise Exception(err)

    if name == BIGRU and not isinstance(preproc, tpp.TextPreprocessor):
        raise ValueError('A valid TextPreprocessor object is required for bigru')
    if name == BIGRU and preproc.ngram_count() != 1:
        raise ValueError('Data should be processed with ngram_range=1 for bigru model.')
    is_bert = U.bert_data_tuple(train_data)
    if is_bert and name != BERT:
        raise ValueError('data is preprocessed for %s but %s was not specified as model' % (BERT, BERT))

    

    # set number of classes and multilabel flag
    x_train = train_data[0]
    y_train = train_data[1]
    if isinstance(y_train[0], int):
        y_train = to_categorical(y_train)
    num_classes = y_train.shape[1]

    # determine multilabel
    if multilabel is None:
        multilabel = U.is_multilabel(train_data)
    if multilabel and name in [NBSVM, LOGREG]:
        warnings.warn('switching to fasttext model, as data suggests '
                      'multilabel classification from data.')
        name = FASTTEXT
    U.vprint("Is Multi-Label? %s" % (multilabel), verbose=verbose)

    # set loss and activations
    loss_func = 'categorical_crossentropy'
    activation = 'softmax'
    if multilabel:
        loss_func = 'binary_crossentropy'
        activation = 'sigmoid'


    # determine number of classes, maxlen, and max_features
    maxlen = U.shape_from_data((x_train, y_train))[1]
    max_features = None
    features = set()
    if not is_bert:
        U.vprint('compiling word ID features...', verbose=verbose)
        for x in x_train:
            features.update(x)
        max_features = len(features)
        U.vprint('max_features is %s' % (max_features), verbose=verbose)
    U.vprint('maxlen is %s' % (maxlen), verbose=verbose)



    # return appropriate model
    if name == LOGREG:
        model =  _build_logreg(x_train, y_train, num_classes, 
                            maxlen,
                            max_features,
                            features,
                            loss_func=loss_func,
                            activation=activation, verbose=verbose)
    elif name == BERT:
        model =  _build_bert(x_train, y_train, num_classes, 
                            maxlen,
                            max_features,
                            features,
                            loss_func=loss_func,
                            activation=activation, verbose=verbose)

    elif name==NBSVM:
        model = _build_nbsvm(x_train, y_train, num_classes, 
                            maxlen,
                            max_features,
                            features,
                            loss_func=loss_func,
                            activation=activation, verbose=verbose)
    elif name==FASTTEXT:
        model = _build_fasttext(x_train, y_train, num_classes, 
                            maxlen,
                            max_features,
                            features,
                            loss_func=loss_func,
                            activation=activation, verbose=verbose)

    elif name==BIGRU:
        (tokenizer, tok_dct) = preproc.get_preprocessor()
        model = _build_bigru(x_train, y_train, num_classes, 
                            maxlen,
                            max_features,
                            features,
                            loss_func=loss_func,
                            activation=activation, verbose=verbose,
                            tokenizer=tokenizer)
    else:
        raise ValueError('name for textclassifier is invalid')
    U.vprint('done.', verbose=verbose)
    return model



def _build_logreg(x_train, y_train, num_classes,
                  maxlen, max_features, features,
                 loss_func='categorical_crossentropy',
                 activation = 'softmax', verbose=1):

    embedding_matrix = np.ones((max_features, 1))
    embedding_matrix[0] = 0

    # set up the model
    inp = Input(shape=(maxlen,))
    r = Embedding(max_features, 1, input_length=maxlen, 
                  weights=[embedding_matrix], trainable=False)(inp)
    x = Embedding(max_features, num_classes, input_length=maxlen, 
                  embeddings_initializer='glorot_normal')(inp)
    x = dot([x,r], axes=1)
    x = Flatten()(x)
    x = Activation(activation)(x)
    model = Model(inputs=inp, outputs=x)
    model.compile(loss=loss_func,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def _build_bert(x_train, y_train, num_classes,
                maxlen, max_features, features,
               loss_func='categorical_crossentropy',
               activation = 'softmax', verbose=1):

    config_path = os.path.join(tpp.get_bert_path(), 'bert_config.json')
    checkpoint_path = os.path.join(tpp.get_bert_path(), 'bert_model.ckpt')

    model = keras_bert.load_trained_model_from_checkpoint(
                                    config_path,
                                    checkpoint_path,
                                    training=True,
                                    trainable=True,
                                    seq_len=maxlen)
    inputs = model.inputs[:2]
    dense = model.get_layer('NSP-Dense').output
    outputs = keras.layers.Dense(units=num_classes, activation='softmax')(dense)
    model = keras.models.Model(inputs, outputs)
    model.compile(loss=loss_func,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model



def _build_nbsvm(x_train, y_train, num_classes,
                 maxlen, max_features, features,
                 loss_func='categorical_crossentropy',
                 activation = 'softmax', verbose=1):

    Y = np.array([np.argmax(row) for row in y_train])
    num_columns = max(features) + 1
    num_rows = len(x_train)

    # set up document-term matrix
    X = csr_matrix((num_rows, num_columns), dtype=np.int8)
    #X = lil_matrix((num_rows, num_columns), dtype=np.int8)
    U.vprint('building document-term matrix... this may take a few moments...',
            verbose=verbose)
    r_ids = []
    c_ids = []
    data = []
    for row_id, row in enumerate(x_train):
        trigger = 10000
        trigger_end =  min(row_id+trigger, num_rows)
        if row_id % trigger == 0: 
            U.vprint('rows: %s-%s' % (row_id+1, trigger_end), 
                     verbose=verbose)
        tmp_c_ids = [column_id for column_id in row if column_id >0 ]
        num = len(tmp_c_ids)
        c_ids.extend(tmp_c_ids)
        r_ids.extend([row_id]* num)
        data.extend([1] * num)
    X = csr_matrix( (data,(r_ids,c_ids)), shape=(num_rows, num_columns) )

    # compute Naive Bayes log-count ratios
    U.vprint('computing log-count ratios...', verbose=verbose)
    nbratios = np.stack([calc_r(i, X, Y).A1 for i in range(num_classes)])
    nbratios = nbratios.T
    embedding_matrix = np.zeros((num_columns, num_classes))
    for i in range(1, num_columns): 
        for j in range(num_classes):
            embedding_matrix[i,j] = nbratios[i,j]

    # set up the model
    inp = Input(shape=(maxlen,))
    r = Embedding(num_columns, num_classes, input_length=maxlen, 
                  weights=[embedding_matrix], trainable=False)(inp)
    x = Embedding(num_columns, 1, input_length=maxlen, 
                  embeddings_initializer='glorot_normal')(inp)
    x = dot([r,x], axes=1)
    x = Flatten()(x)
    x = Activation(activation)(x)
    model = Model(inputs=inp, outputs=x)
    model.compile(loss=loss_func,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def _build_fasttext(x_train, y_train, num_classes,
                 maxlen, max_features, features,
                 loss_func='categorical_crossentropy',
                 activation = 'softmax', verbose=1):

    model = Sequential()
    model.add(Embedding(max_features, 64, input_length=maxlen))
    model.add(SpatialDropout1D(0.25))
    model.add(GlobalMaxPool1D())
    model.add(BatchNormalization())
    model.add(Dense(64, activation='relu', kernel_initializer='he_normal'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation=activation))
    model.compile(loss=loss_func, optimizer='adam', metrics=['accuracy'])

    return model



def get_coefs(word, *arr): return word, np.asarray(arr, dtype='float32')
def _build_bigru(x_train, y_train, num_classes,
                  maxlen, max_features, features,
                 loss_func='categorical_crossentropy',
                 activation = 'softmax', verbose=1,
                 tokenizer=None):


    if tokenizer is None: raise ValueError('bigru requires valid Tokenizer object')

    wv_fpath = tpp.get_wv_path()

    

    # setup pre-trained word embeddings
    embed_size = 300
    U.vprint('processing pretrained word vectors...', verbose=verbose)
    embeddings_index = dict(get_coefs(*o.rstrip().rsplit(' ')) for o in open(wv_fpath))
    word_index = tokenizer.word_index
    nb_words = min(max_features, len(word_index)+1)
    #nb_words = max_features
    embedding_matrix = np.zeros((nb_words, embed_size))
    for word, i in word_index.items():
        if i >= max_features: continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None: embedding_matrix[i] = embedding_vector

    # define model
    inp = Input(shape=(maxlen, ))
    x = Embedding(max_features, embed_size, weights=[embedding_matrix])(inp)
    x = SpatialDropout1D(0.2)(x)
    x = Bidirectional(GRU(80, return_sequences=True))(x)
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPool1D()(x)
    conc = concatenate([avg_pool, max_pool])
    outp = Dense(num_classes, activation=activation)(conc)
    model = Model(inputs=inp, outputs=outp)
    model.compile(loss=loss_func,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model







