package pl.matal;

import java.lang.reflect.Array;

/**
 * Created by aleksander on 26.09.16.
 *
 * Class representing queue for get requests.
 */
public class GetRequestQueue extends RequestQueue<GetRequest> {
    private MemcachedServer server;

    public GetRequestQueue(MemcachedServer server, int workersNumber) {
        this.server = server;
        workers = new Worker[workersNumber];
        for (int i = 0; i < workersNumber; i++) {
            workers[i] = new GetterWorker(this);
        }
    }

    public MemcachedServer getServer() {
        return server;
    }
}
