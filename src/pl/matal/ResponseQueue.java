package pl.matal;

import java.io.IOException;

/**
 * Created by aleksander on 01.10.16.
 */
public class ResponseQueue {
    public static final String SET_SUCCESS_RESPONSE = "STORED";
    public static final String DELETE_SUCCESS_RESPONSE = "DELETED";
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

        } else {
            end.setNext(node);
        }
        for (int i = 0; i < serversNumber; i++) {
            if (positions[i] == null) {
                positions[i] = node;
            }
        }
        end = node;
    }

    public void registerResponse(int serverNumber, String response) {
        // We assume that client sends correct requests.
        // Therefore, positions[serverNumber] here should always be not null.
        // But we check that just in case.
        if (positions[serverNumber] == null) {
            return;
        }
        positions[serverNumber] = positions[serverNumber].registerResponse(response);
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
                if (request.isDelete()) {
                    clientResponse = DELETE_SUCCESS_RESPONSE;
                } else {
                    clientResponse = SET_SUCCESS_RESPONSE;
                }
            } else {
                clientResponse = request.getErrorMessage();
            }
            worker.sendClientResponse(request, clientResponse + "\n");
            worker.logRequest(request);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
