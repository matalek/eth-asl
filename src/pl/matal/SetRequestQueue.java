package pl.matal;

import java.util.List;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetRequestQueue extends RequestQueue {
    public SetRequestQueue(int serverPort) {
        super(serverPort);
        workers = new Worker[1];
        workers[0] = new SetterWorker(this);
    }
}
