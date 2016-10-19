package pl.matal;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

/**
 * Created by aleksander on 28.09.16.
 *
 * Class representing thread forwarding get requests.
 */
public class GetterWorker extends Worker<GetRequestQueue, GetRequest> {
    private PrintWriter out;
    private BufferedReader in;

    public GetterWorker(GetRequestQueue queue) {
        super(queue);
    }

    @Override
    protected void runWorker() throws InterruptedException {
        while (true) {
            GetRequest request = queue.get();
            request.setTime(Request.DEQUEUE_TIME);
            try {
                handleRequest(request);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    protected void connectToServers() throws IOException {
        Socket socket = queue.getServer().connectSync();
        out = new PrintWriter(socket.getOutputStream(), true);
        in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
    }

    @Override
    protected void handleRequest(GetRequest request) throws IOException {
        StringBuilder serverRequest = new StringBuilder("get ");
        serverRequest.append(request.getKey()).append("\r");

        request.setTime(Request.SEND_TO_SERVER_TIME);
        String serverResponse = sendServerRequest(out, in, serverRequest.toString());
        request.setTime(Request.RECEIVE_FROM_SERVER_TIME);
        if (serverResponse.split("\n")[0].contains("ERROR")) {
            request.setSuccessFlag(false);
        }
        sendClientResponse(request, serverResponse);
        logRequest(request);
    }

    private String sendServerRequest(PrintWriter out, BufferedReader in, String serverRequest)
            throws IOException {
        out.println(serverRequest);
        StringBuilder serverResponse = new StringBuilder();
        while (true) {
            String line = in.readLine();
            serverResponse.append(line).append("\n");
            if (line.equals("END") || line.contains("ERROR")) {
                break;
            }
        }
        return serverResponse.toString();
    }
}
