"""CRUD operations for RoommateApproval model."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin'
}


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def send_approval_request(requester_id: int, approver_id: int, room_id: Optional[int] = None) -> Dict[str, Any]:
    """Send a roommate approval request."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "RoommateApproval" ("requesterId", "approverId", "roomId", status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING *
            """,
            (requester_id, approver_id, room_id)
        )
        approval = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return approval
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error sending approval request: {str(e)}")
    finally:
        conn.close()


def get_approval_by_id(approval_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific approval request by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT ra.*,
                   u1.name as "requesterName",
                   u1."registrationNumber" as "requesterRegNo",
                   u2.name as "approverName",
                   u2."registrationNumber" as "approverRegNo",
                   r."roomNumber", r.floor
            FROM "RoommateApproval" ra
            JOIN "User" u1 ON ra."requesterId" = u1.id
            JOIN "User" u2 ON ra."approverId" = u2.id
            LEFT JOIN "Room" r ON ra."roomId" = r.id
            WHERE ra.id = %s
            """,
            (approval_id,)
        )
        approval = cursor.fetchone()
        cursor.close()
        return dict(approval) if approval else None
    except Exception as e:
        raise Exception(f"Error fetching approval by ID: {str(e)}")
    finally:
        conn.close()


def get_pending_requests_for_approver(approver_id: int) -> List[Dict[str, Any]]:
    """Get all pending approval requests for a specific approver."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT ra.*,
                   u.name as "requesterName",
                   u."registrationNumber" as "requesterRegNo",
                   u.rank as "requesterRank",
                   r."roomNumber", r.floor, r."blockId"
            FROM "RoommateApproval" ra
            JOIN "User" u ON ra."requesterId" = u.id
            LEFT JOIN "Room" r ON ra."roomId" = r.id
            WHERE ra."approverId" = %s AND ra.status = 'pending'
            ORDER BY ra."requestedAt" DESC
            """,
            (approver_id,)
        )
        approvals = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return approvals
    except Exception as e:
        raise Exception(f"Error fetching pending requests: {str(e)}")
    finally:
        conn.close()


def get_sent_requests_by_requester(requester_id: int) -> List[Dict[str, Any]]:
    """Get all approval requests sent by a specific requester."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT ra.*,
                   u.name as "approverName",
                   u."registrationNumber" as "approverRegNo",
                   r."roomNumber", r.floor
            FROM "RoommateApproval" ra
            JOIN "User" u ON ra."approverId" = u.id
            LEFT JOIN "Room" r ON ra."roomId" = r.id
            WHERE ra."requesterId" = %s
            ORDER BY ra."requestedAt" DESC
            """,
            (requester_id,)
        )
        approvals = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return approvals
    except Exception as e:
        raise Exception(f"Error fetching sent requests: {str(e)}")
    finally:
        conn.close()


def accept_request(approval_id: int) -> Dict[str, Any]:
    """Accept a roommate approval request."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'approved',
                "respondedAt" = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING *
            """,
            (approval_id,)
        )
        approval = cursor.fetchone()
        if not approval:
            raise Exception("Approval request not found or already responded to")
        approval = dict(approval)
        conn.commit()
        cursor.close()
        return approval
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error accepting request: {str(e)}")
    finally:
        conn.close()


def reject_request(approval_id: int) -> Dict[str, Any]:
    """Reject a roommate approval request."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'rejected',
                "respondedAt" = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING *
            """,
            (approval_id,)
        )
        approval = cursor.fetchone()
        if not approval:
            raise Exception("Approval request not found or already responded to")
        approval = dict(approval)
        conn.commit()
        cursor.close()
        return approval
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error rejecting request: {str(e)}")
    finally:
        conn.close()


def expire_request(approval_id: int) -> Dict[str, Any]:
    """Expire a roommate approval request."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'expired',
                "respondedAt" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (approval_id,)
        )
        approval = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return approval
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error expiring request: {str(e)}")
    finally:
        conn.close()


def check_approval_status(requester_id: int, approver_id: int, room_id: Optional[int] = None) -> Optional[str]:
    """Check if an approval exists and return its status."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if room_id:
            cursor.execute(
                """
                SELECT status FROM "RoommateApproval"
                WHERE "requesterId" = %s AND "approverId" = %s AND "roomId" = %s
                ORDER BY "requestedAt" DESC
                LIMIT 1
                """,
                (requester_id, approver_id, room_id)
            )
        else:
            cursor.execute(
                """
                SELECT status FROM "RoommateApproval"
                WHERE "requesterId" = %s AND "approverId" = %s
                ORDER BY "requestedAt" DESC
                LIMIT 1
                """,
                (requester_id, approver_id)
            )
        result = cursor.fetchone()
        cursor.close()
        return result['status'] if result else None
    except Exception as e:
        raise Exception(f"Error checking approval status: {str(e)}")
    finally:
        conn.close()


def get_approved_roommates(user_id: int) -> List[Dict[str, Any]]:
    """Get all approved roommate relationships for a user (both as requester and approver)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT DISTINCT
                CASE
                    WHEN ra."requesterId" = %s THEN ra."approverId"
                    ELSE ra."requesterId"
                END as "roommateId",
                u.name as "roommateName",
                u."registrationNumber" as "roommateRegNo",
                u.rank as "roommateRank",
                ra."roomId",
                r."roomNumber"
            FROM "RoommateApproval" ra
            JOIN "User" u ON (
                (ra."requesterId" = %s AND u.id = ra."approverId") OR
                (ra."approverId" = %s AND u.id = ra."requesterId")
            )
            LEFT JOIN "Room" r ON ra."roomId" = r.id
            WHERE (ra."requesterId" = %s OR ra."approverId" = %s)
                AND ra.status = 'approved'
            """,
            (user_id, user_id, user_id, user_id, user_id)
        )
        roommates = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return roommates
    except Exception as e:
        raise Exception(f"Error fetching approved roommates: {str(e)}")
    finally:
        conn.close()


def expire_old_pending_requests(hours: int = 24) -> int:
    """Expire pending requests older than specified hours."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'expired',
                "respondedAt" = CURRENT_TIMESTAMP
            WHERE status = 'pending'
                AND "requestedAt" < CURRENT_TIMESTAMP - INTERVAL '%s hours'
            """,
            (hours,)
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error expiring old requests: {str(e)}")
    finally:
        conn.close()


def cancel_request(approval_id: int, user_id: int) -> Dict[str, Any]:
    """Cancel a roommate approval request (only by requester)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'expired'
            WHERE id = %s AND "requesterId" = %s AND status = 'pending'
            RETURNING *
            """,
            (approval_id, user_id)
        )
        approval = cursor.fetchone()
        if not approval:
            raise Exception("Approval request not found, not yours, or already responded to")
        approval = dict(approval)
        conn.commit()
        cursor.close()
        return approval
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error canceling request: {str(e)}")
    finally:
        conn.close()


def get_mutual_approvals(user1_id: int, user2_id: int) -> bool:
    """Check if two users have mutually approved each other."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM "RoommateApproval"
            WHERE (
                ("requesterId" = %s AND "approverId" = %s AND status = 'approved') OR
                ("requesterId" = %s AND "approverId" = %s AND status = 'approved')
            )
            """,
            (user1_id, user2_id, user2_id, user1_id)
        )
        result = cursor.fetchone()
        cursor.close()
        # At least one approval exists
        return result['count'] >= 1
    except Exception as e:
        raise Exception(f"Error checking mutual approvals: {str(e)}")
    finally:
        conn.close()


def bulk_expire_requests_for_user(user_id: int) -> int:
    """Expire all pending requests involving a user (after they get assigned)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE "RoommateApproval"
            SET status = 'expired',
                "respondedAt" = CURRENT_TIMESTAMP
            WHERE status = 'pending'
                AND ("requesterId" = %s OR "approverId" = %s)
            """,
            (user_id, user_id)
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error expiring requests for user: {str(e)}")
    finally:
        conn.close()

