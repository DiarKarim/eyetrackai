using UnityEngine;
using UnityEngine.UI;

public class TeleportController : MonoBehaviour
{
    public GameObject teleportObject;  // The object to teleport

    // Arrays to store the buttons and corresponding target positions
    public Button[] buttons;
    public Transform[] targetPositions;
    public CalibrationManager calibrationManager;


    void Start()
    {
        if (buttons.Length != targetPositions.Length)
        {
            Debug.LogError("Number of buttons and target positions do not match.");
            return;
        }

        for (int i = 0; i < buttons.Length; i++)
        {
            int index = i;  // Capture the loop variable
            buttons[i].onClick.AddListener(() => TeleportTo(index));
        }
    }

    private void TeleportTo(int index)
    {
        calibrationManager._isMoving = false;
        calibrationManager._isStatic = true;

        Vector3 targetPosition = targetPositions[index].position;
        teleportObject.transform.position = new Vector3(targetPosition.x, targetPosition.y, teleportObject.transform.position.z);
        calibrationManager.SendPosition();

    }
}
