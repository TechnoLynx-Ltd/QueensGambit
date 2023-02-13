import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflowjs as tfjs
from model import create_model


def train(model, X_pos_train, X_pos_test, y_scr_train, y_scr_test, tfjs_target_dir):
    history = model.fit(x=X_pos_train,
                        y=y_scr_train,
                        batch_size=128,
                        epochs=1,
                        validation_data=(X_pos_test, y_scr_test),
                        shuffle=True)

    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.5, 1])
    plt.legend(loc='lower right')
    plt.show()

    test_loss, test_acc = model.evaluate(X_pos_test, y_scr_test, verbose=2)

    print(f'Test accuracy {test_acc}')
    tfjs.converters.save_keras_model(model, tfjs_target_dir)
    return model


if __name__ == '__main__':
    X_position = np.load("../../data/npy/X_positions.npy").astype(np.int8)
    y_move = np.load("../../data/npy/y_moves.npy").astype(np.int8)
    y_score = np.load("../../data/npy/y_scores.npy").astype(np.int8)

    X_pos_train, X_pos_test, y_scr_train, y_scr_test = train_test_split(X_position, y_score, test_size=0.1,
                                                                        random_state=42)

    print('Train and test set shapes')
    print(X_pos_train.shape)
    print(X_pos_test.shape)
    print(y_scr_train.shape)
    print(y_scr_test.shape)

    tfjs_target_dir = "../../saved_model_js"

    model = create_model()

    model = train(model, X_pos_train, X_pos_test, y_scr_train, y_scr_test, tfjs_target_dir)

    model.save('')
