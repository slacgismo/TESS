/**
 * SLAC 2019
 * 
 * Created by: jongon
 * 
 * A Modal component that is loaded in the root component. Due to lifecycle triggers,
 * keeping this modal wrapper always loaded prevents race conditions due to mounting 
 * and un-mounting a modal display. The key here is that the this wrapper is, most
 * of the time, simply returning null and not a modal.
 */

 'use strict'

import React from 'react'
import { connect } from 'react-redux'
import Modal from 'react-native-modal'
import { hideModal } from '../actions'
import ModalLogin from './modals/Login'

// All the application modals ought to get registered in this dict for convenience of loading
const MODAL_COMPONENTS = {
    'LOGIN': ModalLogin,
}

class TessModal extends React.PureComponent {
    /**
     * The caller may pass in a custom dismiss handler to perform contextual actions.
     * However, the built in dismissal will always hide the modal, so the caller does 
     * not need to handle hiding the modal.
     */
    dismissHandler = () => {
        if(this.props.modalProps && typeof this.props.modalProps.dismissHandler === 'function') {
            this.props.modalProps.dismissHandler()
        }
        this.props.dispatch(hideModal())
    }

    render() {
        // if no modal type is given, don't display a modal.
        if(!this.props.modalType) {
            return null
        }

        const SpecificModal = MODAL_COMPONENTS[this.props.modalType]

        return(
            <Modal
                isVisible={true}
                onBackdropPress={this.dismissHandler} 
                onBackButtonPress={this.dismissHandler}
                onRequestClose={this.dismissHandler}>
                <SpecificModal {...this.props.modalProps} />
            </Modal>
        )    
    }
}

function mapping(store) {
    return {
        modalType: store.modal.modalType,
        modalProps: store.modal.modalProps
    }
}

export default connect(mapping)(TessModal)