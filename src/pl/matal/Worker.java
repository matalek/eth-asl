package pl.matal;

import java.io.IOException;
import java.nio.ByteBuffer;

/**
 * Created by aleksander on 26.09.16.
 */
public abstract class Worker<Q extends RequestQueue<R>, R extends Request> implements Runnable {
    protected Q queue;
    protected ByteBuffer buffer;

    public Worker(Q queue) {
        this.queue = queue;
        buffer = ByteBuffer.allocate(InputManager.MESSAGE_SIZE);
    }

    @Override
    public void run() {
        try {
            connectToServers();
            runWorker();
        } catch (InterruptedException|IOException e) {
            e.printStackTrace();
        }
    }

    public void sendClientResponse(Request request, String clientResponse) throws IOException {
        buffer.put(clientResponse.getBytes());
        buffer.flip();
        request.setTime(Request.SEND_TO_CLIENT_TIME);
        request.getChannel().write(buffer);
        buffer.clear();
    }

    protected abstract void runWorker() throws InterruptedException;

    protected abstract void connectToServers() throws IOException;

    protected abstract void handleRequest(R request) throws IOException;

    public void logRequest(R request) {
        if (request.isToLog()) {
            MiddlewareServer.getLogger().info(request.getLogString());
        }
    }
}
