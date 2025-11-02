import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, DepthwiseConv2D, SeparableConv2D, BatchNormalization, Activation, AveragePooling2D, Dropout, Reshape, Conv1D, Add, LayerNormalization, Dense
from tensorflow.keras.models import Model

def EEGNet(input_shape, num_classes, dropoutRate=0.5):
    inputs = Input(shape=input_shape)
    x = Conv2D(16, (1, 64), padding='same', use_bias=False)(inputs)
    x = BatchNormalization()(x)
    x = DepthwiseConv2D((input_shape[1], 1), use_bias=False, depth_multiplier=2, padding='valid')(x)
    x = BatchNormalization()(x)
    x = Activation('elu')(x)
    x = AveragePooling2D((1, 4))(x)
    x = Dropout(dropoutRate)(x)
    x = SeparableConv2D(32, (1, 16), padding='same', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('elu')(x)
    x = AveragePooling2D((1, 7))(x)
    x = Dropout(dropoutRate)(x)
    x = Reshape((-1, 32))(x)
    model = Model(inputs=inputs, outputs=x)
    return model

def TCN_Block(x, filters, kernel_size, dilation_rate, dropout_rate=0.1):
    conv1 = Conv1D(filters, kernel_size, padding='causal', dilation_rate=dilation_rate, activation='relu')(x)
    conv1 = LayerNormalization()(conv1)
    conv1 = Dropout(dropout_rate)(conv1)
    conv2 = Conv1D(filters, kernel_size, padding='causal', dilation_rate=dilation_rate, activation='relu')(conv1)
    conv2 = LayerNormalization()(conv2)
    conv2 = Dropout(dropout_rate)(conv2)
    if x.shape[-1] != filters:
        x = Conv1D(filters, 1, padding='same')(x)
    out = Add()([conv2, x])
    out = Activation('relu')(out)
    return out

def build_combined_model(input_shape, num_classes):
    eeg_model = EEGNet(input_shape, num_classes)
    tcn_input = eeg_model.output
    tcn = TCN_Block(tcn_input, filters=64, kernel_size=3, dilation_rate=1)
    tcn = TCN_Block(tcn, filters=64, kernel_size=3, dilation_rate=2)
    tcn = TCN_Block(tcn, filters=64, kernel_size=3, dilation_rate=4)
    x = tf.keras.layers.GlobalAveragePooling1D()(tcn)
    x = Dropout(0.5)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=eeg_model.input, outputs=outputs)
    return model
