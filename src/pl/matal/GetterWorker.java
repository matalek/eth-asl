package pl.matal;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

/**
 * Created by aleksander on 28.09.16.
 */
public class GetterWorker extends Worker {

    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;

    public GetterWorker(RequestQueue queue) {
        super(queue);
    }

    @Override
    public void run() {
        try {
            connectToServer();
            runWorker();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private void connectToServer() throws IOException {
        socket = new Socket("localhost", queue.getServerPort());
        socket.setReuseAddress(true);
        out =
                new PrintWriter(socket.getOutputStream(), true);
        in =
                new BufferedReader(
                        new InputStreamReader(socket.getInputStream()));
    }

    @Override
    protected void handleRequest(Request request) throws IOException {
        StringBuilder serverRequest =  new StringBuilder("get ");
        serverRequest.append(request.getKey()).append("\r");

        // TODO: maybe we want to store value in the object
        // TODO: think about number of lines
        String serverResponse = sendServerRequest(out, in, serverRequest.toString(), 3);
        sendClientResponse(request, serverResponse);
    }
}
