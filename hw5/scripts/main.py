#formulas with matrices
import numpy as np
from numpy.linalg import multi_dot, inv
from math import cos, sin
import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import time

frequency = 100
vmax = 1
vmaxCartesian = 1

amax = 1
amaxCartesian = 1

junction = 5/frequency

def le():
    return [
    670,
    312,
    1075,
    225,
    1280,
    215
 ]

def Tz(l):
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, l],
                         [0, 0, 0, 1]
                         ])

def Tx(l):
        return np.array([[1, 0, 0, l],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]
                         ])

def Ty(l):
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, l],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]
                         ])

def Rx(q):
        return np.array([[1, 0, 0, 0],
                         [0, cos(q), -sin(q), 0],
                         [0, sin(q), cos(q), 0],
                         [0, 0, 0, 1]
                         ])
def lin(Q, des):
    r0 = ((Tbase * FK(Q)))[0:3, 3]
    r0 = transpose(r0)
    r = r0

    delta_q = (np.asarray(des - r0))[0]

    t = np.zeros(3, dtype=np.float)
    T = np.zeros(3, dtype=np.float)
    Tf = np.zeros(3, dtype=np.float)
    Vmax = np.copy(V_cart_max)
    amax = np.copy(a_cart_max)

    for i in range(len(t)):
        if np.sqrt(amax[i] * abs(Q[i])) > Vmax[i]:
            t[i] = Vmax[i] / amax[i]
            T[i] = abs(Q[i]) / Vmax[i]
            Tf[i] = t[i] * 2 + T[i]
        else:
            Vmax[i] = np.sqrt(amax[i] * abs(Q[i]))
            t[i] = np.sqrt(abs(Q[i]) / amax[i])
            T[i] = t[i]
            Tf[i] = 2 * t[i]

    tmax = ceil(max(t) / t_discr) * t_discr
    Tmax = ceil(max(T) / t_discr) * t_discr

    dir = abs(delta_q) / delta_q
    vel_profile = [t[0], T[0], Tf[0], Vmax, amax]

    while prev_time - start_time < vel_profile[2]:
        freq = 0.
        steps = 0

        cur_time = time()
        dt = cur_time - prev_time
        freq += dt
        steps += 1

        QRet = np.zeros(3, dtype=np.float)
        [t, T, Tf, Vmax, amax, trapezia] = traj_params
        for i in range(len(QRet)):
            if trapezia[i]:
                if time <= t:
                    QRet[i] = amax[i] * time
                elif time > t and time <= T:
                    QRet[i] = Vmax[i]
                elif time > T and time <= Tf:
                    QRet[i] = Vmax[i] - amax[i] * (time - T)
                else:
                    QRet[i] = 0
            else:
                if time <= t:
                    QRet[i] = amax[i] * time
                elif time > t and time <= Tf:
                    QRet[i] = Vmax[i] - amax[i] * (time - T)
                else:
                    QRet[i] = 0

        vel = np.assaray(QRet)
        while time() - cur_time < t_discr:
            sleep(0.00001)
        prev_time = cur_time


def Ry(q):
        return np.array([[cos(q), 0, sin(q), 0],
                         [0, 1, 0, 0],
                         [-sin(q), 0, cos(q), 0],
                         [0, 0, 0, 1]
                         ])

def Rz(q):
        return np.array([[cos(q), -sin(q), 0, 0],
                         [sin(q), cos(q), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]
                         ])
def dTx():
    return np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0]])

def dTy():
    return np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0]])


def dTz():
    return np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0]])

def dRx():
    return np.array([[0, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 0]])

def dRy():
    return np.array([[0, 0, 1, 0], [0, 0, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 0]])
def dRz():
    return np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=float)

def FK(q):
    l = le()
    T = multi_dot([Tz(l[0]), Rz(q[0]), Tx(l[1]), Ry(q[1]), Tz(l[2]),
                Ry(q[2]), Tz(l[3]), Tx(l[4]), Rx(q[3]),
                                            Ry(q[4]), Tx(l[5]), Rx(q[5])])
    return T

def j_col(m):
    print(m)
    return np.array([[m[0:3, 3], [m[2, 1]], [m[0, 2]], [m[1, 0]]]]).T


def ptp(Q, des):
    delta_q = (np.asarray(des - Q))
    t = np.zeros(6, dtype=np.float)
    T = np.zeros(6, dtype=np.float)
    Tf = np.zeros(6, dtype=np.float)
    Vmax = np.copy(V_cart_max)
    amax = np.copy(a_cart_max)

    for i in range(len(t)):
        if np.sqrt(amax[i] * abs(Q[i])) > Vmax[i]:
            t[i] = Vmax[i] / amax[i]
            T[i] = abs(Q[i]) / Vmax[i]
            Tf[i] = t[i] * 2 + T[i]
        else:
            Vmax[i] = np.sqrt(amax[i] * abs(Q[i]))
            t[i] = np.sqrt(abs(Q[i]) / amax[i])
            T[i] = t[i]
            Tf[i] = 2 * t[i]

    tmax = ceil(max(t) / t_discr) * t_discr
    Tmax = ceil(max(T) / t_discr) * t_discr
    trapezia = []
    for i in range(len(t)):
        Vmax[i] = abs(Q[i]) / Tmax
        amax[i] = Vmax[i] / tmax
        if np.sqrt(amax[i] * abs(Q[i])) > Vmax[i]:
            t[i] = Vmax[i] / amax[i]
            T[i] = abs(Q[i]) / Vmax[i]
            Tf[i] = T[i] + t[i]
            trapezia.append(True)
        else:
            Vmax[i] = np.sqrt(amax[i] * abs(Q[i]))
            t[i] = np.sqrt(abs(Q[i]) / amax[i])
            T[i] = t[i]
            Tf[i] = 2 * t[i]
            trapezia.append(False)
    dir = abs(delta_q) / delta_q

    vel_profile = [t[0], T[0], Tf[0], Vmax, amax, trapezia]

    while prev_time - start_time < vel_profile[2]:
        freq = 0.
        steps = 0

        cur_time = time()
        dt = cur_time - prev_time
        freq += dt
        steps +=
        QRet = np.zeros(6, dtype=np.float)

        [t, T, Tf, Vmax, amax, trapezia] = traj_params
        for i in range(len(QRet)):
            if trapezia[i]:
                if time <= t:
                    QRet[i] = amax[i] * time
                elif time > t and time <= T:
                    QRet[i] = Vmax[i]
                elif time > T and time <= Tf:
                    QRet[i] = Vmax[i] - amax[i] * (time - T)
                else:
                    QRet[i] = 0
            else:
                if time <= t:
                    QRet[i] = amax[i] * time
                elif time > t and time <= Tf:
                    QRet[i] = Vmax[i] - amax[i] * (time - T)
                else:
                    QRet[i] = 0
        vel = np.assaray(QRet)

        while time() - cur_time < t_discr:
            sleep(0.00001)
        prev_time = cur_time

def jacobian(q, base):
    L = le()

    Tb = np.matrix([[1.0, 0.0, 0.0, base[0]], [0.0, 1.0, 0.0, base[1]], [0.0, 0.0, 1.0, base[2]], [0,0, 0, 1.0]], dtype=float)
    fk = FK(q)
    D_inv = np.linalg.inv(np.matrix(fk))

    T1 = Tb * Rz(q[0]) * dRz() * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * Tz(L[2]) * Rx(q[2]) * Tz(L[3]) * Ry(q[3]) * Ty(
        L[4]) * Rx(q[4]) * Ry(q[5]) * Ty(L[5])
    T2 = Tb * Rz(q[0]) * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * dRx() * Tz(L[2]) * Rx(q[2]) * Tz(L[3]) * Ry(q[3]) * Ty(
        L[4]) * Rx(q[4]) * Ry(q[5]) * Ty(L[5])
    T3 = Tb * Rz(q[0]) * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * Tz(L[2]) * Rx(q[2]) * dRx() * Tz(L[3]) * Ry(q[3]) * Ty(
        L[4]) * Rx(q[4]) * Ry(q[5]) * Ty(L[5])
    T4 = Tb * Rz(q[0]) * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * Tz(L[2]) * Rx(q[2]) * Tz(L[3]) * Ty(L[4]) * Ry(
        q[3]) * dRy() * Rx(q[4]) * Ry(q[5]) * Ty(L[5])
    T5 = Tb * Rz(q[0]) * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * Tz(L[2]) * Rx(q[2]) * Tz(L[3]) * Ry(q[3]) * Ty(L[4]) * Rx(
        q[4]) * dRx() * Ry(q[5]) * Ty(L[5])
    T6 = Tb * Rz(q[0]) * Tz(L[0]) * Ty(L[1]) * Rx(q[1]) * Tz(L[2]) * Rx(q[2]) * Tz(L[3]) * Ry(q[3]) * Ty(L[4]) * Rx(
        q[4]) * Ry(q[5]) * dRy() * Ty(L[5])


    T = [T1, T2, T3, T4, T5, T6]
    J = np.matrix(np.zeros((6, 6)))

    #iterative Jcol( есть не iter выше)
    for i in range(0, 6):
        print(T[i])
        print(T[i][2, 3])
        J[0, i] = T[i][0, 3]
        J[1, i] = T[i][1, 3]
        J[2, i] = T[i][2, 3]
        J[3, i] = (T[i] * D_inv)[2, 1] # умножаем только последгние 3 потому что дл первых inv надо было бы занулитиь
        J[4, i] = (T[i] * D_inv)[0, 2]
        J[5, i] = (T[i] * D_inv)[1, 0]
    return J

def IK(T):
    q = [0,0,0,0,0,0]
    return q




def talker():
    pub = rospy.Publisher('joint_states', JointState, queue_size=10)
    rospy.init_node('joint_state_publisher')
    rate = rospy.Rate(10) # 10hz
    control_str = JointState()
    control_str.header = Header()
    control_str.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']
    control_str.velocity = []
    control_str.effort = []
    control_str.position = [0, np.pi / 2, 0, 0, 0, 0]
    control_str.header.stamp = rospy.Time.now()
    time.sleep(1.5)
    pub.publish(control_str)

    rate.sleep()
    x0, y0, z0 = [float(i) for i in input("Base position: ").split()]
    while not rospy.is_shutdown():
      control_str.position = [float(i) for i in input("Set angle for each joint: ").split()]
      control_str.header.stamp = rospy.Time.now()
      pub.publish(control_str)
      T = FK([0.5, 1.2, 0.5, 1, 0.1, 1.5])
      r = (T * np.transpose(np.matrix([x0, y0, z0, 1])))[0:3]
      print("end effector position: " + str(r))
      rate.sleep()

if __name__ == '__main__':
    L = le()

    idle = np.eye(4)
    t1 = np.concatenate([idle, np.transpose(np.matrix([0, 0, L[0], 1]))], axis=1)
    t2 = np.concatenate([idle, np.transpose(np.matrix([0, L[1], 0, 1]))], axis=1)
    t3 = np.concatenate([idle, np.transpose(np.matrix([0, 0, L[2], 1]))], axis=1)
    t4 = np.concatenate([idle, np.transpose(np.matrix([0, 0, L[3], 1]))], axis=1)
    t5 = np.concatenate([idle, np.transpose(np.matrix([0, L[4], 0, 1]))], axis=1)
    t6 = np.concatenate([idle, np.transpose(np.matrix([0, L[5], 0, 1]))], axis=1)

    try:
        talker()
    except rospy.ROSInterruptException:
        pass
#(jacobian([0,0,0,0.004,0,0], [1.0,0,0.2]))


