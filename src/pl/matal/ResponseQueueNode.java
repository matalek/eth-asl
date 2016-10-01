package pl.matal;

/**
 * Created by aleksander on 01.10.16.
 */
public class ResponseQueueNode {
    private SetRequest request;
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

    public ResponseQueueNode registerResponse() {
        responseCount++;
        return next;
    }

}
