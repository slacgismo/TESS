/**
 * SLAC 2019
 * 
 * Created by: jongon
 * 
 * 
 */

 'use strict'

import React from 'react'
import { connect } from 'react-redux'
import ModalLogin from './modals/Login'
import Modal from 'react-native-modal'
import { hideModal } from '../actions'


const MODAL_COMPONENTS = {
    'LOGIN': ModalLogin,
}

class TessModal extends React.PureComponent {
    dismissHandler = () => {
        if(this.props.modalProps && typeof this.props.modalProps.dismissHandler === 'function') {
            this.props.modalProps.dismissHandler()
        }
        this.props.dispatch(hideModal())
    }

    render() {
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