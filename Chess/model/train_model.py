import matplotlib.pyplot as plt

from Chess.dataset_generation.pgn_dataset import parse_pgn


def train(model, positions, results):
    history = model.fit(positions, results, epochs=10,
                        validation_data=(test_images, test_labels))

    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.5, 1])
    plt.legend(loc='lower right')

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

    print(test_acc)


if __name__ == '__main__':
    X_pos, X_results, moves = parse_pgn('../data/ficsgamesdb_202101_standard2000_nomovetimes_197232.pgn')

    train_model()
