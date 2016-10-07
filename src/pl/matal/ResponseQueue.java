package pl.matal;

import java.io.IOException;

/**
 * Created by aleksander on 01.10.16.
 */
public class ResponseQueue {
    private int serversNumber;
    private SetterWorker worker;
    private ResponseQueueNode start, end;
    private ResponseQueueNode positions[];

    public ResponseQueue(int serversNumber, SetterWorker worker) {
        this.serversNumber = serversNumber;
        this.worker = worker;
        positions = new ResponseQueueNode[serversNumber];
    }

    public void addRequest(SetRequest request) {
        ResponseQueueNode node = new ResponseQueueNode(request, null);
        if (start == null) {
            start = node;
            for (int i = 0; i < serversNumber; i++) {
                positions[i] = start;
            }
        } else {
            end.setNext(node);
        }
        end = node;
    }

    public void registerResponse(int serverNumber, boolean success) {
        positions[serverNumber] = positions[serverNumber].registerResponse(success);
        check();
    }

    private void check() {
        while (start != null && start.getResponseCount() == serversNumber) {
            respondToClient(start.getRequest());
            start = start.getNext();
        }
    }

    private void respondToClient(SetRequest request) {
        try {
            request.setTime(Request.RECEIVE_FROM_SERVER_TIME);
            String clientResponse;
            if (request.getSuccessFlag()) {
                clientResponse = "STORED";
            } else {
                // TODO: what to do if there was an error
                clientResponse = "NOT_STORED";
            }
            worker.sendClientResponse(request, clientResponse + "\n");
            worker.logRequest(request);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
