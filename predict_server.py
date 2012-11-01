import argparse, tempfile
from liblinearutil import *
from twisted.internet import protocol, reactor, threads

def doPredict(data, model_, probability_estimates):
    tf = tempfile.NamedTemporaryFile()
    tf.write(data)
    tf.flush()

    _, x = svm_read_problem(tf.name)
    tf.close()

    p_label, _, p_val = predict([], x, model_, '-b ' + ('1' if probability_estimates else '0'))

    return 'labels {0}\n{1:d} {2}'.format(' '.join(map(repr, range(1, len(p_val[0]) + 1))), int(p_label[0]), ' '.join(map(lambda x: '{0:.6g}'.format(x), p_val[0])))

class Prediction(protocol.Protocol):
    def onProcessDone(self, result):
        self.message(result)
        self.transport.loseConnection()

    def onError(self, result):
        self.message("Error: " + result.getErrorMessage())

    def processFunction(self, data):
        return doPredict(data, self.factory.model_, self.factory.probability_estimates)

    def dataReceived(self, data):
        deferred = threads.deferToThread(self.processFunction, data)
        deferred.addCallback(self.onProcessDone)
        deferred.addErrback(self.onError)

    def message(self, message):
        self.transport.write(message + '\n')

class PredictionFactory(protocol.Factory):
    protocol = Prediction

    def __init__(self, model_, probability_estimates):
        self.model_ = model_
        self.probability_estimates = probability_estimates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type = int, help = 'port number to listen on')
    parser.add_argument('model_file', help = 'model file')
    parser.add_argument('-b', '--probability_estimates', action = 'store_true', default = False, help = 'whether to output probability estimates (default False); currently for logistic regression only')
    args = parser.parse_args()

    print 'Loading model...'
    model_ = load_model(args.model_file)
    print 'Ready'

    reactor.listenTCP(args.port, PredictionFactory(model_, args.probability_estimates))
    reactor.run()

if __name__ == "__main__":
    main()
