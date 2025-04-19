import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QDoubleSpinBox, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QDialog, QDialogButtonBox,
                             QDateEdit, QFormLayout)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models import engine, Usuario, Transaccion, Credencial
import re

Session = sessionmaker(bind=engine)

class RegistroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro de Usuario")
        layout = QFormLayout()
        
        # Campos de usuario
        self.nombre_input = QLineEdit()
        layout.addRow("Nombre:", self.nombre_input)
        
        self.apellido_input = QLineEdit()
        layout.addRow("Apellido:", self.apellido_input)
        
        self.rut_input = QLineEdit()
        layout.addRow("RUT:", self.rut_input)
        
        self.email_input = QLineEdit()
        layout.addRow("Email:", self.email_input)
        
        self.telefono_input = QLineEdit()
        layout.addRow("Teléfono:", self.telefono_input)
        
        self.fecha_nacimiento_input = QDateEdit()
        self.fecha_nacimiento_input.setCalendarPopup(True)
        self.fecha_nacimiento_input.setDate(QDate.currentDate())
        layout.addRow("Fecha de Nacimiento:", self.fecha_nacimiento_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Contraseña:", self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Confirmar Contraseña:", self.confirm_password_input)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validar_registro)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def validar_rut(self, rut):
        rut = rut.replace(".", "").replace("-", "").upper()
        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            return False
        return True
        
    def validar_registro(self):
        # Validaciones básicas
        if not all([self.nombre_input.text(), self.apellido_input.text(),
                   self.rut_input.text(), self.email_input.text(),
                   self.telefono_input.text(), self.password_input.text()]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        if not self.validar_rut(self.rut_input.text()):
            QMessageBox.warning(self, "Error", "RUT inválido")
            return
            
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return
            
        self.accept()
        
    def get_datos(self):
        return {
            'nombre': self.nombre_input.text(),
            'apellido': self.apellido_input.text(),
            'rut': self.rut_input.text(),
            'email': self.email_input.text(),
            'telefono': self.telefono_input.text(),
            'fecha_nacimiento': self.fecha_nacimiento_input.date().toPython(),
            'password': self.password_input.text()
        }

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Iniciar Sesión")
        layout = QFormLayout()
        
        self.email_input = QLineEdit()
        layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Contraseña:", self.password_input)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validar_login)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Botón de registro
        registro_btn = QPushButton("Registrarse")
        registro_btn.clicked.connect(self.registrarse)
        layout.addRow(registro_btn)
        
        self.setLayout(layout)
        
    def validar_login(self):
        if not self.email_input.text() or not self.password_input.text():
            QMessageBox.warning(self, "Error", "Email y contraseña son obligatorios")
            return
            
        self.accept()
        
    def registrarse(self):
        registro_dialog = RegistroDialog(self)
        if registro_dialog.exec() == QDialog.Accepted:
            datos = registro_dialog.get_datos()
            session = Session()
            
            # Verificar si el email ya existe
            if session.query(Credencial).filter_by(email=datos['email']).first():
                QMessageBox.warning(self, "Error", "El email ya está registrado")
                return
                
            # Crear usuario
            usuario = Usuario(
                nombre=datos['nombre'],
                apellido=datos['apellido'],
                email=datos['email'],
                rut=datos['rut'],
                telefono=datos['telefono'],
                fecha_nacimiento=datos['fecha_nacimiento']
            )
            session.add(usuario)
            session.flush()
            
            # Crear credenciales
            credencial = Credencial(
                usuario_id=usuario.id,
                email=datos['email'],
                password_hash=Credencial.hash_password(datos['password'])
            )
            session.add(credencial)
            
            session.commit()
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente")
            
    def get_datos(self):
        return {
            'email': self.email_input.text(),
            'password': self.password_input.text()
        }

class EditarTransaccionDialog(QDialog):
    def __init__(self, transaccion, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Transacción")
        self.transaccion = transaccion
        
        layout = QVBoxLayout()
        
        # Descripción
        self.descripcion_input = QLineEdit(transaccion.descripcion)
        layout.addWidget(QLabel("Descripción:"))
        layout.addWidget(self.descripcion_input)
        
        # Monto
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setPrefix("$")
        self.monto_input.setRange(-1000000, 1000000)
        self.monto_input.setValue(transaccion.monto)
        layout.addWidget(QLabel("Monto:"))
        layout.addWidget(self.monto_input)
        
        # Tipo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Ingreso", "Gasto"])
        self.tipo_combo.setCurrentText(transaccion.tipo)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.tipo_combo)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_datos(self):
        return {
            'descripcion': self.descripcion_input.text(),
            'monto': self.monto_input.value(),
            'tipo': self.tipo_combo.currentText()
        }

class FinanzasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finanzas Personales - Chile")
        self.setGeometry(100, 100, 800, 600)
        
        self.session = Session()
        self.usuario_actual = None
        
        self.iniciar_sesion()
        
    def iniciar_sesion(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == QDialog.Accepted:
            datos = login_dialog.get_datos()
            
            # Verificar credenciales
            credencial = self.session.query(Credencial).filter_by(email=datos['email']).first()
            if not credencial or not credencial.verificar_password(datos['password']):
                QMessageBox.warning(self, "Error", "Email o contraseña incorrectos")
                self.iniciar_sesion()
                return
                
            self.usuario_actual = credencial.usuario
            self.inicializar_interfaz()
        else:
            sys.exit()
            
    def inicializar_interfaz(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Información del usuario
        usuario_info = QLabel(f"Bienvenido, {self.usuario_actual.nombre} {self.usuario_actual.apellido}")
        usuario_info.setStyleSheet("font-size: 16px;")
        layout.addWidget(usuario_info)
        
        # Balance total
        self.balance_label = QLabel("Balance Total: $0")
        self.balance_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.balance_label)
        
        # Formulario para agregar transacciones
        form_layout = QHBoxLayout()
        
        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción")
        form_layout.addWidget(self.descripcion_input)
        
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setPrefix("$")
        self.monto_input.setRange(-1000000, 1000000)
        form_layout.addWidget(self.monto_input)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Ingreso", "Gasto"])
        form_layout.addWidget(self.tipo_combo)
        
        agregar_btn = QPushButton("Agregar")
        agregar_btn.clicked.connect(self.agregar_transaccion)
        form_layout.addWidget(agregar_btn)
        
        layout.addLayout(form_layout)
        
        # Tabla de transacciones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Descripción", "Monto", "Tipo", "Acciones"])
        layout.addWidget(self.tabla)
        
        # Cargar transacciones
        self.cargar_transacciones()
        
    def cargar_transacciones(self):
        if not self.usuario_actual:
            return
            
        transacciones = self.session.query(Transaccion).filter_by(usuario_id=self.usuario_actual.id).all()
        self.tabla.setRowCount(len(transacciones))
        
        balance = 0
        for i, transaccion in enumerate(transacciones):
            self.tabla.setItem(i, 0, QTableWidgetItem(transaccion.fecha.strftime("%d/%m/%Y %H:%M")))
            self.tabla.setItem(i, 1, QTableWidgetItem(transaccion.descripcion))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"${transaccion.monto:,.0f}".replace(",", ".")))
            self.tabla.setItem(i, 3, QTableWidgetItem(transaccion.tipo))
            
            # Botones de acciones
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda checked, t=transaccion: self.editar_transaccion(t))
            acciones_layout.addWidget(editar_btn)
            
            borrar_btn = QPushButton("Borrar")
            borrar_btn.clicked.connect(lambda checked, t=transaccion: self.borrar_transaccion(t))
            acciones_layout.addWidget(borrar_btn)
            
            self.tabla.setCellWidget(i, 4, acciones_widget)
            
            # Actualizar balance
            if transaccion.tipo == "Ingreso":
                balance += transaccion.monto
            else:
                balance -= transaccion.monto
                
        self.balance_label.setText(f"Balance Total: ${balance:,.0f}".replace(",", "."))
        self.tabla.resizeColumnsToContents()
        
    def agregar_transaccion(self):
        descripcion = self.descripcion_input.text()
        monto = self.monto_input.value()
        tipo = self.tipo_combo.currentText()
        
        if not descripcion:
            QMessageBox.warning(self, "Error", "Por favor ingrese una descripción")
            return
            
        transaccion = Transaccion(
            descripcion=descripcion,
            monto=monto,
            tipo=tipo,
            usuario_id=self.usuario_actual.id
        )
        
        self.session.add(transaccion)
        self.session.commit()
        
        self.cargar_transacciones()
        
        # Limpiar inputs
        self.descripcion_input.clear()
        self.monto_input.setValue(0)
        
    def editar_transaccion(self, transaccion):
        dialog = EditarTransaccionDialog(transaccion, self)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.get_datos()
            transaccion.descripcion = datos['descripcion']
            transaccion.monto = datos['monto']
            transaccion.tipo = datos['tipo']
            
            self.session.commit()
            self.cargar_transacciones()
            
    def borrar_transaccion(self, transaccion):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro que desea borrar esta transacción?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session.delete(transaccion)
            self.session.commit()
            self.cargar_transacciones()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanzasApp()
    window.show()
    sys.exit(app.exec())
