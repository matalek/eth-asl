package pl.matal;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

/**
 * Created by aleksander on 28.09.16.
 */
public class GetterWorker extends Worker<GetRequestQueue, GetRequest> {
    private PrintWriter out;
    private BufferedReader in;

    public GetterWorker(GetRequestQueue queue) {
        super(queue);
    }

    @Override
    public void run() {
        try {
            connectToServer();
            runWorker();
        } catch (InterruptedException|IOException e) {
            e.printStackTrace();
        }
    }

    private void connectToServer() throws IOException {
        Socket socket = queue.getServer().connectSync();
        out = new PrintWriter(socket.getOutputStream(), true);
        in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
    }

    @Override
    protected void handleRequest(GetRequest request) throws IOException {
        StringBuilder serverRequest = new StringBuilder("get ");
        serverRequest.append(request.getKey()).append("\r");

        // TODO: maybe we want to store value in the object
        // TODO: think about number of lines
        String serverResponse = sendServerRequest(out, in, serverRequest.toString());
        sendClientResponse(request, serverResponse);
    }

    private String sendServerRequest(PrintWriter out, BufferedReader in, String serverRequest)
            throws IOException {
        out.println(serverRequest);
        StringBuilder serverResponse = new StringBuilder();
        while (true) {
            String line = in.readLine();
            serverResponse.append(line).append("\n");
            if (line.equals("END")) {
                break;
            }
        }
        return serverResponse.toString();
    }
}
