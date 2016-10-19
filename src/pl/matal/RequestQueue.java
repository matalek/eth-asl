package pl.matal;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Created by aleksander on 26.09.16.
 *
 * Class representing queue in which requests are stored.
 */
public abstract class RequestQueue<R extends Request> {
    protected BlockingQueue<R> queue;
    protected Worker[] workers;

    public RequestQueue() {
        this.queue = new LinkedBlockingQueue<R>();
    }

    public void add(R request) {
        // Queue has no size limitations, so we don't block here.
        queue.add(request);
    }

    public R get() throws InterruptedException {
        // Queue can be empty, so we need a blocking version here.
        return queue.take();
    }

    // Non-blocking version for setter worker.
    public R getNoBlock() throws InterruptedException {
        return queue.poll();
    }

    public void startWorkers() {
        for (Worker worker : workers) {
            new Thread(worker).start();
        }
    }
}
