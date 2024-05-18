import asyncio
import json
import pygame
from go2_webrtc import Go2Connection, ROBOT_CMD

# Initialization of pygame and joystick
pygame.init()
pygame.joystick.init()
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
except pygame.error:
    print("No joystick connected!")

DEADZONE = 0.11

def gen_command(cmd):
    return json.dumps({"type": "msg", "topic": "rt/api/sport/request",
                       "data": {"header": {"identity": {"id": Go2Connection.generate_id(), "api_id": cmd}},
                                "parameter": json.dumps(cmd)}})

def gen_move_command(x, y, z):
    return json.dumps({"type": "msg", "topic": "rt/api/sport/request",
                       "data": {"header": {"identity": {"id": Go2Connection.generate_id(), "api_id": ROBOT_CMD["Move"]}},
                                "parameter": json.dumps({"x": x, "y": y, "z": z})}})

async def joystick_loop(conn, sensitivity=0.5):
    await conn.connect_robot()
    while True:
        pygame.event.pump()
        if pygame.joystick.get_count() > 0:
            data = {"Left V": joystick.get_axis(0) * -1, "Left H": joystick.get_axis(1) * -1,
                    "Right V": joystick.get_axis(3) * -1, "Right H": joystick.get_axis(2) * -1,
                    "R Trigger": joystick.get_axis(5), "L Trigger": joystick.get_axis(4),
                    **{f"{btn}": joystick.get_button(i) for i, btn in enumerate("ABXY")}}

            for k, v in data.items():
                if "Trigger" not in k and abs(v) <= DEADZONE:
                    data[k] = 0

            sensitivity = 2 if data["R Trigger"] > 0.5 else 0.5
            joy_move_x, joy_move_y, joy_move_z = data["Right V"] * sensitivity, data["Right H"] * sensitivity, data["Left V"] * sensitivity

            if any(data[btn] for btn in "ABXY"):
                robot_cmd = gen_command(ROBOT_CMD["Pose"] if data["X"] else ROBOT_CMD["Hello"])
                conn.data_channel.send(robot_cmd)

            if abs(joy_move_x) > 0 or abs(joy_move_y) > 0 or abs(joy_move_z) > 0:
                robot_cmd = gen_move_command(joy_move_x, joy_move_y, joy_move_z)
                conn.data_channel.send(robot_cmd)

        await asyncio.sleep(0.1)

async def main():
    conn = Go2Connection("192.168.12.1", "<your_jwt_token_here>")
    try:
        await joystick_loop(conn)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping...")
    finally:
        await conn.pc.close()

if __name__ == "__main__":
    asyncio.run(main())
