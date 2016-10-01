package pl.matal;

/**
 * Created by aleksander on 26.09.16.
 */
public class GetRequestQueue extends RequestQueue {

    public GetRequestQueue(int serverPort) {
        super(serverPort);
        // TODO: add more workers
        workers = new Worker[1];
        workers[0] = new GetterWorker(this);
    }
}
