import os
import asyncio
import jwt
import datetime
from db import get_conn
import proto.attendance_pb2 as pb2
import proto.attendance_pb2_grpc as pb2_grpc
from jwt_utils import verify_token

class AttendanceServicer(pb2_grpc.AttendanceServiceServicer):

    async def List(self, request, context):
        try:
            verify_token(request.jwt)
        except Exception:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid JWT")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, employee_id, action, timestamp FROM attendance WHERE employee_id=%s ORDER BY timestamp DESC",
            (request.employee_id,)
        )
        for r in cur.fetchall():
            yield pb2.AttendanceRecord(
                id=r[0],
                employee_id=r[1],
                action=r[2],
                timestamp=r[3].isoformat()
            )
        cur.close(); conn.close()

    async def StreamNew(self, request, context):
        try:
            verify_token(request.jwt)
        except Exception:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid JWT")

        i = 0
        while True:
            i += 1
            record = pb2.AttendanceRecord(
                id=i,
                employee_id="emp1",
                action="in",
                timestamp=datetime.datetime.utcnow().isoformat()
            )
            yield record
            await asyncio.sleep(5) 

async def serve():
    server = grpc.aio.server()
    pb2_grpc.add_AttendanceServiceServicer_to_server(AttendanceServicer(), server)
    server.add_insecure_port(f"[::]:{int(os.getenv('ATTENDANCE_GRPC_PORT', 50051))}")
    await server.start()
    print("Async gRPC server started.")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())