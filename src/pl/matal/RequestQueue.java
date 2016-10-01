package pl.matal;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingDeque;
import java.util.concurrent.LinkedBlockingDeque;

/**
 * Created by aleksander on 26.09.16.
 */
public abstract class RequestQueue<R> {
    protected BlockingDeque<R> queue;
    protected Worker[] workers;

    public RequestQueue() {
        this.queue = new LinkedBlockingDeque<>();
    }

    public void add(R request) {
        // Queue has no size limitations, so we don't block here.
        queue.add(request);
    }

    public R get() throws InterruptedException {
        // Queue can be empty, so we need a blocking version here.
        return queue.take();
    }

    public R getNoBlock() throws InterruptedException {
        // TODO: Non-blocking versiob - remove after changing to not active waiting
        return queue.poll();
    }

    public void startWorkers() {
        for (Worker worker : workers) {
            new Thread(worker).start();
        }
    }
}
