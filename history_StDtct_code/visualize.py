from time import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


def get_data():
    # data = np.load('A.npy')
    # label = np.arange(1034)
    data = np.load('V.npy')
    label = np.load("train_video_identities.npy")
    # data = data[:100]
    # label = label[:100]
    n_samples, n_features = data.shape
    return data, label, n_samples, n_features


def plot_embedding(data, label, title):
    x_min, x_max = np.min(data, 0), np.max(data, 0)
    data = (data - x_min) / (x_max - x_min)

    fig = plt.figure()
    ax = plt.subplot(111)
    for i in range(data.shape[0]):
        plt.text(data[i, 0], data[i, 1], str(label[i]),
                 color=plt.cm.Set1(label[i] / 1034.),
                 fontdict={'weight': 'bold', 'size': 9})
    plt.xticks([])
    plt.yticks([])
    plt.title(title)
    plt.savefig('V.png')
    return fig


def main():
    data, label, n_samples, n_features = get_data()
    print('Computing t-SNE embedding')
    tsne = TSNE(n_components=2, random_state=0)
    t0 = time()
    result = tsne.fit_transform(data)
    fig = plot_embedding(result, label,
                         't-SNE embedding of the videos (time %.2fs)'
                         % (time() - t0))
    # plt.show(fig)


if __name__ == '__main__':
    main()