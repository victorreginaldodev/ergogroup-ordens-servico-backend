from django.db import models


class TipoUsuario(models.TextChoices):
    # Thiago e Amanda
    DIRETOR = 'diretor', 'Diretor'
    # Comercial
    GESTOR_COMERCIAL = 'gestor_comercial', 'Gestor Comercial'
    COMERCIAL = 'comercial', 'Comercial'
    # Área Técnica
    GESTOR_TECNICO = 'gestor_tecnico', 'Líder Técnico'
    SUB_GESTOR_TECNICO = 'sub_gestor_tecnico', 'Sub-Líder Técnico'
    TECNICO = 'tecnico', 'Técnico'
    # Financeiro
    GESTOR_FINANCEIRO = 'gestor_financeiro', 'Gestor Financeiro'
    FINANCEIRO = 'financeiro', 'Financeiro'
    # Administrativo
    GESTOR_ADMINISTRATIVO = 'gestor_administrativo', 'Gestor Administrativo'
    ADMINISTRATIVO = 'administrativo', 'Administrativo'