"""
Модуль автоматизации (Automation Engine)
Применяет правила автоматизации к тикетам
"""
from sqlalchemy.orm import Session
from app import models
import json
from typing import Dict, Any
from datetime import datetime

def evaluate_condition(condition: Dict[str, Any], ticket: models.Ticket) -> bool:
    """
    Оценить одно условие
    condition: {"field": "priority", "operator": "equals", "value": "critical"}
    """
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    
    # Получаем значение поля из тикета
    if field == "priority":
        ticket_value = ticket.priority
    elif field == "status":
        ticket_value = ticket.status_rel.name if ticket.status_rel else None
    elif field == "category":
        ticket_value = ticket.category
    elif field == "company_id":
        ticket_value = ticket.company_id
    elif field == "created_by":
        ticket_value = ticket.created_by
    elif field == "title":
        ticket_value = ticket.title
    elif field == "description":
        ticket_value = ticket.description or ""
    else:
        return False
    
    # Операторы сравнения
    if operator == "equals":
        return ticket_value == value
    elif operator == "not_equals":
        return ticket_value != value
    elif operator == "contains":
        return value.lower() in (ticket_value or "").lower()
    elif operator == "not_contains":
        return value.lower() not in (ticket_value or "").lower()
    elif operator == "in":
        return ticket_value in (value if isinstance(value, list) else [value])
    elif operator == "is_empty":
        return not ticket_value
    elif operator == "is_not_empty":
        return bool(ticket_value)
    
    return False

def evaluate_conditions(conditions: Dict[str, Any], ticket: models.Ticket) -> bool:
    """
    Оценить все условия
    conditions: {
        "all": [condition1, condition2],
        "any": [condition3]
    }
    """
    # По умолчанию - AND между всеми условиями
    match_type = conditions.get("match_type", "all")
    condition_list = conditions.get("conditions", [])
    
    if not condition_list:
        return True
    
    results = [evaluate_condition(c, ticket) for c in condition_list]
    
    if match_type == "all":
        return all(results)
    elif match_type == "any":
        return any(results)
    
    return False

def execute_action(action: Dict[str, Any], ticket: models.Ticket, db: Session, tenant_id: int):
    """
    Выполнить одно действие
    action: {"action": "set_priority", "value": "high"}
    """
    action_type = action.get("action")
    value = action.get("value")
    
    if action_type == "set_priority":
        ticket.priority = value
        
    elif action_type == "set_status":
        # Найти ID статуса по имени
        status = db.query(models.TicketStatus).filter(
            models.TicketStatus.tenant_id == tenant_id,
            models.TicketStatus.name == value
        ).first()
        if status:
            ticket.status_id = status.id
            
    elif action_type == "assign_agent":
        ticket.assigned_to = value
        
    elif action_type == "add_tags":
        current_tags = ticket.tags or []
        new_tags = value if isinstance(value, list) else [value]
        ticket.tags = list(set(current_tags + new_tags))
        
    elif action_type == "set_category":
        ticket.category = value
        
    elif action_type == "send_notification":
        # Создать уведомление
        notification = models.Notification(
            tenant_id=tenant_id,
            user_id=value,
            type="automation",
            title="Автоматическое действие",
            message=f"Тикет #{ticket.readable_id}: {action.get('message', 'Выполнено автоматическое действие')}"
        )
        db.add(notification)
        
    elif action_type == "add_internal_note":
        # Добавить приватную заметку
        note = models.InternalNote(
            tenant_id=tenant_id,
            ticket_id=ticket.id,
            user_id=None,  # Системная заметка
            content=value,
            is_pinned=False
        )
        db.add(note)

def apply_automation_rules(ticket: models.Ticket, db: Session, tenant_id: int, event: str = "ticket_created"):
    """
    Применить все активные правила автоматизации к тикету
    event: "ticket_created" или "ticket_updated"
    """
    # Получаем все активные правила для тенанта
    rules = db.query(models.AutomationRule).filter(
        models.AutomationRule.tenant_id == tenant_id,
        models.AutomationRule.is_active == True
    ).order_by(models.AutomationRule.order).all()
    
    for rule in rules:
        conditions = rule.conditions or {}
        actions = rule.actions or {}
        
        # Проверяем подходит ли событие
        rule_events = conditions.get("events", ["ticket_created"])
        if event not in rule_events:
            continue
        
        # Оцениваем условия
        if evaluate_conditions(conditions, ticket):
            # Выполняем действия
            action_list = actions.get("actions", [])
            for action in action_list:
                try:
                    execute_action(action, ticket, db, tenant_id)
                except Exception as e:
                    print(f"Error executing automation action: {e}")
            
            # Добавляем в timeline
            timeline = models.TicketTimeline(
                tenant_id=tenant_id,
                ticket_id=ticket.id,
                user_id=None,
                event_type="automation_applied",
                content=json.dumps({
                    "rule_name": rule.name,
                    "rule_id": rule.id
                })
            )
            db.add(timeline)
            
            # Если правило настроено на остановку - прекращаем выполнение
            if actions.get("stop_processing", False):
                break

def check_sla_breach(ticket: models.Ticket, db: Session):
    """
    Проверить нарушение SLA и отправить уведомления
    """
    if not ticket.sla_due_at:
        return
    
    now = datetime.utcnow()
    time_remaining = ticket.sla_due_at - now
    
    # Если осталось меньше 1 часа - срочное уведомление
    if time_remaining.total_seconds() < 3600 and time_remaining.total_seconds() > 0:
        if ticket.assigned_to:
            notification = models.Notification(
                tenant_id=ticket.tenant_id,
                user_id=ticket.assigned_to,
                type="sla_warning",
                title="⚠️ SLA скоро истекает!",
                message=f"Тикет #{ticket.readable_id}: Осталось менее 1 часа до дедлайна"
            )
            db.add(notification)
    
    # Если SLA просрочено
    elif time_remaining.total_seconds() < 0:
        # Уведомляем агента
        if ticket.assigned_to:
            notification = models.Notification(
                tenant_id=ticket.tenant_id,
                user_id=ticket.assigned_to,
                type="sla_breach",
                title="🚨 SLA нарушен!",
                message=f"Тикет #{ticket.readable_id}: Дедлайн просрочен"
            )
            db.add(notification)
        
        # Уведомляем администраторов
        admins = db.query(models.User).filter(
            models.User.tenant_id == ticket.tenant_id,
            models.User.role.in_([models.UserRole.ADMIN, models.UserRole.SUPER_ADMIN])
        ).all()
        
        for admin in admins:
            notification = models.Notification(
                tenant_id=ticket.tenant_id,
                user_id=admin.id,
                type="sla_breach",
                title="🚨 SLA нарушен!",
                message=f"Тикет #{ticket.readable_id}: Дедлайн просрочен для агента {ticket.assignee.full_name if ticket.assignee else 'Unknown'}"
            )
            db.add(notification)