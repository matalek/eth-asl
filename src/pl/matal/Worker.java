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
public abstract class Worker implements Runnable {
    protected RequestQueue queue;

    public Worker(RequestQueue queue) {
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
            Request request = queue.get();

            try {
                handleRequest(request);
//                request.getChannel().close();
            } catch (IOException e) {
                e.printStackTrace();
            } // TODO: maybe add finally

        }
    }

    protected String sendServerRequest(PrintWriter out, BufferedReader in, String serverRequest, int responseLinesCount)
            throws IOException {
        out.println(serverRequest);
        StringBuilder serverResponse = new StringBuilder();
        for (int i = 0; i < responseLinesCount; i++) {
            serverResponse.append(in.readLine()).append("\n");
        }
        return serverResponse.toString();
    }

    protected void sendClientResponse(Request request, String clientResponse) throws IOException {
        ByteBuffer buffer = ByteBuffer.allocate(2048); // TODO: think about size
        buffer.put(clientResponse.getBytes());
        buffer.flip();
        request.getChannel().write(buffer);
    }

    protected abstract void handleRequest(Request request) throws IOException;
}
