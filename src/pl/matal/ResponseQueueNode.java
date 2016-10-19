package pl.matal;

/**
 * Created by aleksander on 01.10.16.
 *
 * Class representing single node in the response queue.
 */
public class ResponseQueueNode {
    private SetRequest request;
    // Counts how many responses for this requesy we have received.
    private int responseCount = 0;
    private ResponseQueueNode next;

    public ResponseQueueNode(SetRequest request, ResponseQueueNode next) {
        this.request = request;
        this.next = next;
    }

    public SetRequest getRequest() {
        return request;
    }

    public int getResponseCount() {
        return responseCount;
    }

    public ResponseQueueNode getNext() {
        return next;
    }

    public void setNext(ResponseQueueNode next) {
        this.next = next;
    }

    // If error message is empty, request has succeeded.
    public ResponseQueueNode registerResponse(String response) {
        boolean success;
        if (request.isDelete()) {
            // We assume that if the key to be deleted was not found, then it's an error.
            success = response.equals(ResponseQueue.DELETE_SUCCESS_RESPONSE);
        } else {
            success = response.equals(ResponseQueue.SET_SUCCESS_RESPONSE);
        }
        if (!success) {
            request.setSuccessFlag(false);
            request.setErrorMessage(response);
        }
        responseCount++;
        return next;
    }
}
