package pl.matal;

import java.lang.reflect.Array;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetRequestQueue extends RequestQueue<SetRequest> {
    private MemcachedServer[] servers;

    public SetRequestQueue(MemcachedServer[] servers) {
        this.servers = servers;
        workers = new Worker[1];
        workers[0] = new SetterWorker(this);
    }

    public MemcachedServer[] getServers() {
        return servers;
    }
}
