from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash

"""
calculate the percentage between two numbers
"""

def percentage_calculate(input_num, base_num):
    return (base_num / input_num) * 100