using UnityEngine;
using System.Collections;
using UnityEngine.SceneManagement;
using UnityEditor.EditorTools;
using System;

public class CalibrationManager : MonoBehaviour
{
    [Header("Reference")]
    [Tooltip("The Object we want to move through a path.")]
    [SerializeField] GameObject target;

    [Tooltip("The parent of the points they are under.")]
    [SerializeField] GameObject points;

    [Tooltip("UDP Communication")]
    [SerializeField] UDPCommunication UDPCommunication;

    [Header("Movement Settings")]
    [Tooltip("The order of points we want the Target to follow.")]
    [SerializeField] Transform[] pathPoints;

    [Tooltip("How fast the target moves to points.")]
    [SerializeField] float speed = 2f;

    [Tooltip("How long should it stay at a point before moving to the next.")]
    [SerializeField] float delay = 0.5f;

    [Tooltip("Velocity profile curve, 0 to 1 time on x-axis and 0 to 1 velocity factor on y-axis.")]
    [SerializeField] AnimationCurve velocityProfile = AnimationCurve.EaseInOut(0, 0, 1, 1);


    private int _currentPointIndex = 0;
    private bool _movingForward = true;
    private bool _isWaiting = false;

    [Header("Buttons")]
    public bool _isMoving = false;
    public bool _isStatic = false;
    private float _distanceToNextPoint;
    private float _distanceCovered;

    void Start()
    {
        if (pathPoints.Length > 0)
        {
            target.transform.position = pathPoints[0].position;
            _distanceToNextPoint = Vector3.Distance(target.transform.position, pathPoints[_currentPointIndex].position);
        }
    }

    void Update()
    {
        if (pathPoints.Length == 0 || target == null || _isWaiting || !_isMoving) return;

        Vector3 targetPosition = target.transform.position;
        Vector3 destinationPosition = pathPoints[_currentPointIndex].position;

        _distanceCovered += speed * Time.deltaTime;
        float t = _distanceCovered / _distanceToNextPoint;
        float velocityFactor = velocityProfile.Evaluate(t);

        target.transform.position = Vector3.MoveTowards(targetPosition, destinationPosition, speed * velocityFactor * Time.deltaTime);

        if (Vector3.Distance(target.transform.position, destinationPosition) < 0.1f)
        {
            string pointID = pathPoints[_currentPointIndex].gameObject.name;
            UDPCommunication.SendUDPMessage($"Reached Point {pointID}");
            StartCoroutine(WaitAtPoint());
        }

        SendPosition();

    }

    private IEnumerator WaitAtPoint()
    {
        _isWaiting = true;
        yield return new WaitForSeconds(delay);

        if (_movingForward)
        {
            _currentPointIndex++;
            if (_currentPointIndex >= pathPoints.Length)
            {
                // Stop the movement when reaching the last point
                _isMoving = false;
                _currentPointIndex = 0;
                yield break;
            }
        }

        _distanceToNextPoint = Vector3.Distance(target.transform.position, pathPoints[_currentPointIndex].position);
        _distanceCovered = 0;
        _isWaiting = false;
    }

    public void SetInvisible()
    {
        points.SetActive(!points.activeSelf); // Sets the visibility of the points if needed
    }

    public void ToggleMovement()
    {
        if (_isStatic)
        {
            Reset();
        }

        _isMoving = !_isMoving;
    }

    public void Reset()
    {
        _currentPointIndex = 0; // Reset the index
        target.transform.position = pathPoints[0].position; // Reset the position of the target
        _distanceToNextPoint = Vector3.Distance(target.transform.position, pathPoints[_currentPointIndex].position);
        _distanceCovered = 0;
        _isMoving = false;
        _isStatic = false;
    }

    public void SendPosition()
    {
        UDPCommunication.SendUDPMessage($"{Math.Round(target.transform.position.x, 1)},{Math.Round(target.transform.position.y, 1)}");
    }
}
