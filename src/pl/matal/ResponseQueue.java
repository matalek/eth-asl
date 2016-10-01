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

    public void registerResponse(int serverNumber) {
        positions[serverNumber] = positions[serverNumber].registerResponse();
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
            // TODO: change response
            worker.sendClientResponse(request, "STORED\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
