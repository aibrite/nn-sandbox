from aibrite.ml.neuralnet import NeuralNet
import numpy as np


class NeuralNetWithAdam(NeuralNet):

    def __repr__(self):
        return ("NeuralNetWithAdam[it={iteration_count},lr={learning_rate:6.4f},hl={hidden_layers},"
                "lrd={learning_rate_decay:6.4f}, lambd={lambd:6.4f},"
                "batch={minibatch_size}, epochs={epochs},"
                "shuffle={shuffle}, beta1={beta1:6.4f},"
                "beta2={beta2: 6.4f}, epsilon={epsilon:6.4f}]").format(iteration_count=self.iteration_count,
                                                                       learning_rate=self.learning_rate,
                                                                       hidden_layers=self.hidden_layers,
                                                                       learning_rate_decay=self.learning_rate_decay,
                                                                       lambd=self.lambd,
                                                                       minibatch_size=self.minibatch_size,
                                                                       epochs=self.epochs,
                                                                       shuffle=self.shuffle,
                                                                       beta1=self.beta1,
                                                                       beta2=self.beta2,
                                                                       epsilon=self.epsilon)

    def initialize_layers(self):
        super().initialize_layers()
        for i, layer in enumerate(self._hidden_layers + [self.output_layer]):
            layer.VdW = np.zeros(layer.W.shape)
            layer.Vdb = np.zeros(layer.b.shape)
            layer.SdW = np.zeros(layer.W.shape)
            layer.Sdb = np.zeros(layer.b.shape)

    def _backward_for_layer(self, layer, Y, iteration_data):
        super()._backward_for_layer(layer, Y, iteration_data)
        layer.VdW = self.beta1 * layer.VdW + \
            (1.0 - self.beta1) * layer.dW
        layer.Vdb = self.beta1 * layer.Vdb + \
            (1.0 - self.beta1) * layer.db
        layer.SdW = self.beta2 * layer.SdW + \
            (1.0 - self.beta2) * np.square(layer.dW)
        layer.Sdb = self.beta2 * layer.Sdb + \
            (1.0 - self.beta2) * np.square(layer.db)

        t = iteration_data.total_batch_index
        layer.VdWCorrected = layer.VdW / (1 - self.beta1)**t
        layer.VdbCorrected = layer.Vdb / (1 - self.beta1)**t

        layer.SdWCorrected = layer.SdW / (1 - self.beta2)**t
        layer.SdbCorrected = layer.Sdb / (1 - self.beta2)**t

    def _grad_layer(self, layer, Y, iteration_data):
        lr = iteration_data.calculated_learning_rate
        layer.W = layer.W - lr * \
            (layer.VdWCorrected /
             (np.sqrt(layer.SdWCorrected) + self.epsilon))

        layer.b = layer.b - lr * \
            (layer.VdbCorrected /
             (np.sqrt(layer.SdbCorrected) + self.epsilon))

    def get_hyperparameters(self):
        hp = super().get_hyperparameters()
        hp['beta1'] = self.beta1
        hp['beta2'] = self.beta2
        hp['epsilon'] = self.epsilon

        return hp

    def __init__(self, train_x, train_y, beta1=0.9, beta2=0.999, epsilon=0.00000001, *args, **kwargs):
        super().__init__(train_x, train_y, *args, **kwargs)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
