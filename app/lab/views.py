import arrow
from flask import render_template, url_for, request, flash, redirect, make_response
from flask_login import login_required, current_user
from . import lab_blueprint as lab
from .forms import *
from .models import *
from app.main.models import UserLabAffil
from collections import namedtuple

TestOrder = namedtuple('TestOrder', ['order', 'ordered_at', 'type', 'approved_at'])


@lab.route('/<int:lab_id>')
@login_required
def landing(lab_id):
    affil = UserLabAffil.query.filter_by(lab_id=lab_id, user_id=current_user.id).first()
    if not affil or not affil.approved:
        flash('You do not have a permission to enter this lab.', 'danger')
        return redirect(url_for('main.index'))
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/index.html', lab=lab)


@lab.route('/labs', methods=['GET', 'POST'])
@login_required
def create_lab():
    form = LabForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            lab = Laboratory()
            form.populate_obj(lab)
            lab.creator = current_user
            db.session.add(lab)
            db.session.commit()
            flash('Your new lab has been created.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Error happened.', 'danger')
    return render_template('lab/lab_form.html', form=form)


@lab.route('/<int:lab_id>/tests')
@login_required
def list_tests(lab_id):
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/test_list.html', lab=lab)


@lab.route('/<int:lab_id>/choice_sets')
@login_required
def list_choice_sets(lab_id):
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/choice_set_list.html', lab=lab)


@lab.route('/<int:lab_id>/choice_sets/<int:choice_set_id>/items', methods=['GET', 'POST'])
@lab.route('/<int:lab_id>/choice_sets/<int:choice_set_id>/items/<int:choice_item_id>', methods=['GET', 'POST'])
@login_required
def add_choice_item(lab_id, choice_set_id, choice_item_id=None):
    if choice_item_id:
        item = LabResultChoiceItem.query.get(choice_item_id)
        form = ChoiceItemForm(obj=item)
    else:
        form = ChoiceItemForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not choice_item_id:
                item = LabResultChoiceItem()
            form.populate_obj(item)
            item.choice_set_id = choice_set_id
            db.session.add(item)
            activity = LabActivity(
                lab_id=lab_id,
                actor=current_user,
                message='Added result choice item',
                detail=item.result,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            db.session.add(activity)
            db.session.commit()
            flash('New choice has been added.', 'success')
        else:
            flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('lab.list_choice_sets', lab_id=lab_id))
    return render_template('lab/new_choice_item.html', form=form)


@lab.route('/result-sets/items/<int:choice_item_id>', methods=['DELETE'])
@login_required
def remove_choice_item(choice_item_id):
    item = LabResultChoiceItem.query.get(choice_item_id)
    resp = make_response()
    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        resp.headers['HX-Reswap'] = 'none'
    return resp


@lab.route('/<int:lab_id>/choice_sets/add', methods=['GET', 'POST'])
@lab.route('/<int:lab_id>/choice_sets/<int:choice_set_id>', methods=['GET', 'POST'])
@login_required
def add_choice_set(lab_id, choice_set_id=None):
    if choice_set_id:
        choice_set = LabResultChoiceSet.query.get(choice_set_id)
        form = ChoiceSetForm(obj=choice_set)
    else:
        form = ChoiceSetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not choice_set_id:
                choice_set = LabResultChoiceSet()
            form.populate_obj(choice_set)
            choice_set.lab_id = lab_id
            db.session.add(choice_set)
            activity = LabActivity(
                lab_id=lab_id,
                message='Added a new choice set',
                detail=choice_set.name,
                added_at=arrow.now('Asia/Bangkok').datetime,
                actor=current_user
            )
            db.session.add(activity)
            db.session.commit()
            flash('New choice set has been added.', 'success')
        else:
            flash('Error occurred while adding a new choice set.', 'danger')
        return redirect(url_for('lab.list_choice_sets', lab_id=lab_id))
    return render_template('lab/new_choice_set.html', form=form)


@lab.route('/<int:lab_id>/choice_sets/<int:choice_set_id>/remove')
@login_required
def remove_choice_set(lab_id, choice_set_id):
    choiceset = LabResultChoiceSet.query.get(choice_set_id)
    if choiceset:
        db.session.delete(choiceset)
        db.session.commit()
        flash('The choice set has been removed.', 'success')
    else:
        flash('The choice set does not exist.', 'warning')
    return redirect(url_for('lab.list_choice_sets', lab_id=lab_id))


@lab.route('/<int:lab_id>/quantests/add', methods=['GET', 'POST'])
@login_required
def add_test(lab_id):
    form = LabTestForm(lab_id=lab_id)
    form.choice_set.query = LabResultChoiceSet.query.filter_by(lab_id=lab_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_test = LabTest()
            form.populate_obj(new_test)
            new_test.lab_id = lab_id
            new_test.added_at = arrow.now('Asia/Bangkok').datetime
            db.session.add(new_test)
            activity = LabActivity(
                lab_id=lab_id,
                actor=current_user,
                message='Added a new quantitative test',
                detail=form.name.data,
                added_at=arrow.now('Asia/Bangkok').datetime,
            )
            db.session.add(activity)
            db.session.commit()
            flash('New quantative test has been added.')
            return redirect(url_for('lab.list_tests', lab_id=lab_id))
        else:
            flash(form.errors, 'danger')
    return render_template('lab/new_test.html', form=form)


@lab.route('/<int:lab_id>/quantests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_test(lab_id, test_id):
    test = LabTest.query.get(test_id)
    form = LabTestForm(obj=test)
    form.choice_set.query = LabResultChoiceSet.query.filter_by(lab_id=lab_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(test)
            db.session.add(test)
            db.session.commit()
            flash('Data have been saved.', 'success')
            return redirect(url_for('lab.list_tests', lab_id=lab_id))
        else:
            flash('An error occurred. Please contact the system administrator.', 'danger')
    return render_template('lab/new_test.html', form=form, lab_id=lab_id)


@lab.route('/<int:lab_id>/quantests/<int:test_id>/remove', methods=['GET', 'POST'])
@login_required
def remove_quan_test(lab_id, test_id):
    if not current_user.is_affiliated_with(lab_id):
        flash('You do not have a permission to perform this task.', 'danger')

    test = LabTest.query.get(test_id)
    db.session.delete(test)
    db.session.commit()
    flash('The record has been removed along with its associated records.', 'success')
    return redirect(request.referrer)


@lab.route('/<int:lab_id>/customers')
@login_required
def list_patients(lab_id):
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/customer_list.html', lab=lab)


@lab.route('/<int:lab_id>/patients/add', methods=['GET', 'POST'])
@lab.route('/<int:lab_id>/patients/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add_patient(lab_id, customer_id=None):
    if customer_id:
        customer = LabCustomer.query.get(customer_id)
        form = LabCustomerForm(obj=customer)
    else:
        form = LabCustomerForm()
    lab = Laboratory.query.get(lab_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            if not customer:
                customer = LabCustomer()
            form.populate_obj(customer)
            customer.lab_id = lab_id
            db.session.add(customer)
            activity = LabActivity(
                lab_id=lab_id,
                actor=current_user,
                message='Added a new patient',
                detail=customer.fullname,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            db.session.add(activity)
            db.session.commit()
            if customer_id:
                flash('Customer info has been updated.', 'success')
            else:
                flash('New customer has been added.', 'success')
            return render_template('lab/customer_list.html', lab=lab)
        else:
            flash('Failed to add a new customer.', 'danger')
    return render_template('lab/new_customer.html', form=form, lab_id=lab_id)


@lab.route('/<int:lab_id>/patients/<int:customer_id>/orders', methods=['GET', 'POST'])
@lab.route('/<int:lab_id>/patients/<int:customer_id>/orders/<int:order_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def add_test_order(lab_id, customer_id, order_id=None):
    lab = Laboratory.query.get(lab_id)
    selected_test_ids = []
    order = None
    if order_id:
        order = LabTestOrder.query.get(order_id)
        selected_test_ids = [record.test.id for record in order.test_records]
    if request.method == 'DELETE':
        order.cancelled_at = arrow.now('Asia/Bangkok').datetime
        for rec in order.test_records:
            rec.cancelled = True
            db.session.add(rec)
        activity = LabActivity(
            lab_id=lab_id,
            actor=current_user,
            message='Cancelled an order.',
            detail=order.id,
            added_at=arrow.now('Asia/Bangkok').datetime
        )
        db.session.add(order)
        db.session.add(activity)
        db.session.commit()
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    if request.method == 'POST':
        form = request.form
        test_ids = form.getlist('test_ids')
        if not order_id:
            order = LabTestOrder(
                lab_id=lab_id,
                customer_id=customer_id,
                ordered_at=arrow.now('Asia/Bangkok').datetime,
                ordered_by=current_user,
                test_records=[LabTestRecord(test_id=tid) for tid in test_ids],
            )
            activity = LabActivity(
                lab_id=lab_id,
                actor=current_user,
                message='Added an order.',
                detail=order.id,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            flash('New order has been added.', 'success')
        else:
            updated_test_records = []
            for test_id in test_ids:
                if test_id not in selected_test_ids:
                    updated_test_records.append(LabTestRecord(test_id=test_id))
                else:
                    test_record = LabTestRecord.query.filter_by(order_id=order_id, test_id=test_id).one()
                    updated_test_records.append(test_record)
            for test_id in selected_test_ids:
                if test_id not in test_ids:
                    test_record = LabTestRecord.query.filter_by(order_id=order_id, test_id=test_id).one()
                    test_record.cancelled = True
                    db.session.add(test_record)
                    activity = LabActivity(
                        lab_id=lab_id,
                        actor=current_user,
                        message='Cancelled a test order.',
                        detail=test_record.id,
                        added_at=arrow.now('Asia/Bangkok').datetime
                    )
                    db.session.add(activity)

            order.test_records = updated_test_records
            activity = LabActivity(
                lab_id=lab_id,
                actor=current_user,
                message='Updated an order.',
                detail=order.id,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            flash('The order has been updated.', 'success')

        db.session.add(order)
        db.session.add(activity)
        db.session.commit()
        return redirect(url_for('lab.show_customer_test_records',
                                customer_id=customer_id, order_id=order.id))
    return render_template('lab/new_test_order.html',
                           lab=lab,
                           order=order,
                           customer_id=customer_id,
                           selected_test_ids=selected_test_ids)


@lab.route('/<int:lab_id>/orders', methods=['GET', 'POST'])
@login_required
def list_test_orders(lab_id):
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/test_order_list.html', lab=lab)


@lab.route('/<int:lab_id>/orders/quan/<int:order_id>/cancel', methods=['GET', 'POST'])
@login_required
def cancel_test_order(lab_id, order_id):
    order = LabTestOrder.query.get(order_id)
    order.cancelled_at = arrow.now('Asia/Bangkok').datetime
    order.cancelled_by = current_user
    db.session.add(order)
    activity = LabActivity(
        lab_id=lab_id,
        actor=current_user,
        message='Cancelled the quantitative test order.',
        detail=order.id,
        added_at=arrow.now('Asia/Bangkok').datetime
    )
    db.session.add(activity)
    db.session.commit()
    flash('The order has been cancelled.', 'success')
    if request.args.get('pending'):
        return redirect(url_for('lab.list_pending_orders', lab_id=lab_id))
    return redirect(url_for('lab.list_test_orders', lab_id=lab_id))


# TODO: deprecated
@lab.route('/records/<int:record_id>/reject', methods=['GET', 'POST'])
@login_required
def reject_test_order(record_id):
    record = LabTestRecord.query.get(record_id)
    form = LabOrderRejectRecordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_record = LabOrderRejectRecord()
            form.populate_obj(new_record)
            new_record.created_at = arrow.now('Asia/Bangkok').datetime
            new_record.creator = current_user
            record.reject_record = new_record
            record.cancelled_at = True
            db.session.add(record)
            db.session.add(new_record)
            activity = LabActivity(
                lab_id=record.order.lab_id,
                actor=current_user,
                message='Rejected and cancelled the test order.',
                detail=record.id,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            db.session.add(activity)
            db.session.commit()
            flash('The test has been rejected.', 'success')
            return redirect(url_for('lab.list_test_orders', lab_id=record.order.lab_id))
        else:
            flash('{}. Please contact the system admin.'.format(form.errors), 'danger')
    return render_template('lab/order_reject.html', form=form)


@lab.route('/records/<int:record_id>/receive', methods=['GET', 'POST'])
@login_required
def receive_test_order(record_id):
    record = LabTestRecord.query.get(record_id)
    record.received_at = arrow.now('Asia/Bangkok').datetime
    record.receiver = current_user
    db.session.add(record)
    activity = LabActivity(
        lab_id=record.order.lab_id,
        actor=current_user,
        message='Received the test.',
        detail=record.id,
        added_at=arrow.now('Asia/Bangkok').datetime
    )
    db.session.add(activity)
    db.session.commit()
    flash('The order has been received.', 'success')
    return redirect(url_for('lab.show_customer_test_records',
                            order_id=record.order_id, customer_id=record.order.customer.id))


@lab.route('/<int:lab_id>/orders/pending', methods=['GET', 'POST'])
@login_required
def list_pending_orders(lab_id):
    lab = Laboratory.query.get(lab_id)
    pendings = LabTestRecord.query.filter_by(updated_at=None)
    pendings = [r for r in pendings if r.order.lab_id==lab_id]
    return render_template('lab/pending_orders.html', lab=lab, pendings=pendings)


@lab.route('/<int:lab_id>/activities')
@login_required
def list_activities(lab_id):
    lab = Laboratory.query.get(lab_id)
    return render_template('lab/log.html', lab=lab)


@lab.route('/customers/<int:customer_id>/records')
@login_required
def show_customer_records(customer_id):
    customer = LabCustomer.query.get(customer_id)
    if customer:
        return render_template('lab/customer_records.html', customer=customer)


@lab.route('/customers/<int:customer_id>/orders/<int:order_id>/records')
@login_required
def show_customer_test_records(customer_id, order_id):
    customer = LabCustomer.query.get(customer_id)
    order = LabTestOrder.query.get(order_id)
    return render_template('lab/recordset_detail.html', customer=customer, order=order)


@lab.route('/orders/<int:order_id>/records/<int:record_id>', methods=['POST', 'GET'])
@login_required
def finish_test_record(order_id, record_id):
    order = LabTestOrder.query.get(order_id)
    rec = LabTestRecord.query.get(record_id)
    if not order or not rec:
        flash('The order or the test record no longer exists.', 'danger')
        return redirect(request.referrer)

    LabTestRecordForm = create_lab_test_record_form(rec.test, default=rec.text_result)
    form = LabTestRecordForm(obj=rec)

    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(rec)
            rec.updated_at = arrow.now('Asia/Bangkok').datetime
            rec.updater = current_user
            if form.choice_set.data:
                rec.text_result = form.choice_set.data.result
            activity = LabActivity(
                lab_id=order.lab_id,
                actor=current_user,
                message='Added the result for a test record.',
                detail=rec.id,
                added_at=arrow.now('Asia/Bangkok').datetime
            )
            order.finished_at = arrow.now('Asia/Bangkok').datetime
            db.session.add(rec)
            db.session.add(activity)
            db.session.commit()
            flash('New result record has been saved.', 'success')
            return redirect(url_for('lab.show_customer_test_records', order_id=order_id, customer_id=order.customer.id))
        else:
            flash(form.errors, 'danger')
    return render_template('lab/new_test_record.html', form=form, order=order, rec=rec)



@lab.route('/orders/<int:order_id>/approve')
@login_required
def approve_test_order(order_id):
    order = LabTestOrder.query.get(order_id)
    order.approved_at = arrow.now('Asia/Bangkok').datetime
    order.approver = current_user
    db.session.add(order)
    db.session.commit()
    resp = make_response()
    resp.headers['HX-Refresh'] = 'true'
    return resp


@lab.route('/labs/<int:lab_id>/rejects')
@login_required
def list_rejected_orders(lab_id):
    lab = Laboratory.query.get(lab_id)
    records = []
    for order in lab.test_orders:
        for record in order.test_records:
            if record.reject_record:
                records.append(record)
    return render_template('lab/reject_records.html', records=records, lab=lab)


@lab.route('/records/<int:record_id>/revisions')
@login_required
def test_record_revisions(record_id):
    record = LabTestRecord.query.get(record_id)
    return render_template('lab/test_revisions.html', record=record)
