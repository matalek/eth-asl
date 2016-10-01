package pl.matal;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 26.09.16.
 */
public abstract class Worker<Q extends RequestQueue<R>, R> implements Runnable {
    protected Q queue;

    public Worker(Q queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
        try {
            runWorker();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    protected void runWorker() throws InterruptedException {
        while (true) {
            R request = queue.get();

            try {
                handleRequest(request);
//                request.getChannel().close();
            } catch (IOException e) {
                e.printStackTrace();
            } // TODO: maybe add finally

        }
    }

    public void sendClientResponse(Request request, String clientResponse) throws IOException {
        ByteBuffer buffer = ByteBuffer.allocate(2048); // TODO: think about size
        buffer.put(clientResponse.getBytes());
        buffer.flip();
        request.getChannel().write(buffer);
    }

    protected abstract void handleRequest(R request) throws IOException;
}
