import matplotlib.pyplot as plt

from Chess.dataset_generation.pgn_dataset import load_all_pgn
from Chess.model.model import create_model


def train(model, X_pos_train, X_pos_test, y_scr_train, y_scr_test):

    history = model.fit(x=X_pos_train,
                        y=y_scr_train,
                        batch_size=128,
                        epochs=10,
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

    print(test_acc)


if __name__ == '__main__':
    (X_pos_train, X_pos_test), (y_scr_train, y_scr_test) = load_all_pgn()

    model = create_model()

    train(model, X_pos_train, X_pos_test, y_scr_train, y_scr_test)
