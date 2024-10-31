using UnityEngine;

// Responsible for UDP communication
using System.Net.Sockets;
using System.Text;
using System;

public class UDPCommunication : MonoBehaviour
{
    [SerializeField] Transform targetTransform;
    [SerializeField] Transform cameraTransform;
    [SerializeField] string serverIP = "127.0.0.1";
    [SerializeField] int port = 8000;
    private UdpClient _client;

    private void Start()
    {
        _client = new UdpClient();
        Debug.Log("UDP Client Created");
    }

    private void Update()
    {
        // Debug.Log("SendMessage called");
        SendMessage($"{Math.Round(targetTransform.position.x, 2)},{Math.Round(targetTransform.position.y, 2)}");
    }
    void SendMessage(string message)
    {
        if (_client != null) // Making sure there is a client to use
        {
            try
            {
                byte[] data = Encoding.UTF8.GetBytes(message); // Encodes the message into Bytes
                _client.Send(data, data.Length, serverIP, port);
                Debug.Log($"The message \"{message}\" has been sent");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error sending message: {e.Message}");
            }

        }
    }
}
