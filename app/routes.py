from flask import render_template, flash, redirect, url_for, request
from app import app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from app.models import User, Machine, Part, PartHistory, UserActivity
from app.forms import LoginForm, RegistrationForm, AddMachineForm, AddPartForm, ConsumePartForm

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return redirect(url_for('main.machines'))

@bp.route('/machines')
@login_required
def machines():
    machines = Machine.query.all()
    return render_template('machines.html', title='Machines', machines=machines)

@bp.route('/machine/<int:machine_id>')
@login_required
def machine_parts(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    parts = machine.parts.all()
    return render_template('parts.html', title=machine.name, machine=machine, parts=parts)

@bp.route('/add_machine', methods=['GET', 'POST'])
@login_required
def add_machine():
    form = AddMachineForm()
    if form.validate_on_submit():
        machine = Machine(name=form.name.data, description=form.description.data)
        db.session.add(machine)
        db.session.commit()
        
        # Log activity
        activity = UserActivity(user_id=current_user.id, 
                              action=f'Added machine: {machine.name}')
        db.session.add(activity)
        db.session.commit()
        
        flash('Machine added successfully!')
        return redirect(url_for('main.machines'))
    return render_template('add_machine.html', title='Add Machine', form=form)

@bp.route('/delete_machine/<int:machine_id>', methods=['POST'])
@login_required
def delete_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    
    # Log activity
    activity = UserActivity(user_id=current_user.id, 
                          action=f'Deleted machine: {machine.name}')
    db.session.add(activity)
    
    db.session.delete(machine)
    db.session.commit()
    flash('Machine deleted successfully!')
    return redirect(url_for('main.machines'))

@bp.route('/add_part', methods=['GET', 'POST'])
@login_required
def add_part():
    form = AddPartForm()
    if form.validate_on_submit():
        part = Part(
            name=form.name.data,
            part_number=form.part_number.data,
            total_received=form.total_received.data,
            machine_id=form.machine.data
        )
        db.session.add(part)
        
        # Add to history
        history = PartHistory(
            part_id=part.id,
            action='added',
            quantity=form.total_received.data
        )
        db.session.add(history)
        
        # Log activity
        activity = UserActivity(user_id=current_user.id, 
                              action=f'Added part: {part.name} ({part.part_number})')
        db.session.add(activity)
        
        db.session.commit()
        flash('Part added successfully!')
        return redirect(url_for('main.machine_parts', machine_id=form.machine.data))
    return render_template('add_part.html', title='Add Part', form=form)

@bp.route('/delete_part/<int:part_id>', methods=['POST'])
@login_required
def delete_part(part_id):
    part = Part.query.get_or_404(part_id)
    machine_id = part.machine_id
    
    # Log activity
    activity = UserActivity(user_id=current_user.id, 
                          action=f'Deleted part: {part.name} ({part.part_number})')
    db.session.add(activity)
    
    db.session.delete(part)
    db.session.commit()
    flash('Part deleted successfully!')
    return redirect(url_for('main.machine_parts', machine_id=machine_id))

@bp.route('/consume_part/<int:part_id>', methods=['GET', 'POST'])
@login_required
def consume_part(part_id):
    part = Part.query.get_or_404(part_id)
    form = ConsumePartForm()
    
    if form.validate_on_submit():
        if form.quantity.data > part.available:
            flash('Cannot consume more than available quantity!')
            return redirect(url_for('main.consume_part', part_id=part.id))
            
        part.consumed += form.quantity.data
        
        # Add to history
        history = PartHistory(
            part_id=part.id,
            action='consumed',
            quantity=form.quantity.data,
            notes=form.notes.data
        )
        db.session.add(history)
        
        # Log activity
        activity = UserActivity(user_id=current_user.id, 
                              action=f'Consumed {form.quantity.data} of {part.name} ({part.part_number})')
        db.session.add(activity)
        
        db.session.commit()
        flash('Part consumption recorded!')
        return redirect(url_for('main.machine_parts', machine_id=part.machine_id))
    
    return render_template('consume_part.html', title='Consume Part', part=part, form=form)

@bp.route('/part_history/<int:part_id>')
@login_required
def part_history(part_id):
    part = Part.query.get_or_404(part_id)
    history = part.history.order_by(PartHistory.timestamp.desc()).all()
    return render_template('history.html', title=f'{part.name} History', part=part, history=history)

@bp.route('/activity_log')
@login_required
def activity_log():
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).all()
    return render_template('activity_log.html', title='Activity Log', activities=activities)



@app.route('/')
def index():
    return render_template('index.html')
