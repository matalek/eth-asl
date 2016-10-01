package pl.matal;

/**
 * Created by aleksander on 26.09.16.
 */
public class GetRequestQueue extends RequestQueue {

    public GetRequestQueue(int serverPort, int workersNumber) {
        super(serverPort);
        workers = new Worker[workersNumber];
        for (int i = 0; i < workersNumber; i++) {
            workers[i] = new GetterWorker(this);
        }
    }
}
