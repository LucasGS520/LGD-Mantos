from app.shared.models.entities import Revision


def audit(db, entity_type, entity_id, action, reason, before, after):
    db.add(
        Revision(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            reason=reason,
            before=before,
            after=after,
        )
    )
