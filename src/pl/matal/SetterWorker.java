package pl.matal;

import com.sun.xml.internal.bind.v2.runtime.reflect.Accessor;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetterWorker extends Worker {

    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;

    public SetterWorker(RequestQueue queue) {
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
        SetRequest setRequest = (SetRequest) request;
        StringBuilder serverRequest =  new StringBuilder("set ");
        serverRequest.append(request.getKey()).append(" ");
        for (int i = 0; i < 3; i++) {
            serverRequest.append(setRequest.getParams()[i]).append(" ");
        }
        serverRequest.append("\r\n");
        serverRequest.append(setRequest.getValue());
        serverRequest.append("\r");

        String serverResponse = sendServerRequest(out, in, serverRequest.toString(), 1);
        sendClientResponse(request, serverResponse);
    }
}
