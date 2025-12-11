from datetime import date, datetime

from flask import Flask, jsonify, request


def calculate_nc_year_from_age(age: int) -> int | None:
    """
    Very simplified NC year calculation.

    Assumes age is the child's age at the start of the academic year
    and returns a National Curriculum year between 0 and 11.
    For this demo we use: NCY = age - 4, clamped to [0, 11].
    """
    if age < 4 or age > 15:
        return None

    nc_year = age - 4
    return max(0, min(nc_year, 11))


def calculate_age_from_dob(dob_str: str) -> int | None:
    """
    Parse an ISO date string (YYYY-MM-DD) and return age in years.
    Uses today's date for simplicity.
    """
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return None

    today = date.today()
    years = today.year - dob.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1

    if years < 0:
        return None
    return years


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "Admissions Eligibility Checker API",
                "endpoints": ["/year?age=", "/year-from-dob?dob=", "/health"],
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/year")
    def year_from_age():
        """
        Example: GET /year?age=10 -> {"age": 10, "nc_year": 6}
        """
        age_param = request.args.get("age")
        if age_param is None:
            return jsonify({"error": "age query parameter is required"}), 400

        try:
            age = int(age_param)
        except ValueError:
            return jsonify({"error": "age must be an integer"}), 400

        nc_year = calculate_nc_year_from_age(age)
        if nc_year is None:
            return jsonify({"error": "age out of supported range"}), 400

        return jsonify({"age": age, "nc_year": nc_year})

    @app.get("/year-from-dob")
    def year_from_dob():
        """
        Example: GET /year-from-dob?dob=2015-09-12
        -> {"dob": "2015-09-12", "age": 10, "nc_year": 6}
        """
        dob = request.args.get("dob")
        if dob is None:
            return jsonify({"error": "dob query parameter is required"}), 400

        age = calculate_age_from_dob(dob)
        if age is None:
            return jsonify({"error": "dob must be a valid past date in YYYY-MM-DD format"}), 400

        nc_year = calculate_nc_year_from_age(age)
        if nc_year is None:
            return jsonify({"error": "age out of supported range"}), 400

        return jsonify({"dob": dob, "age": age, "nc_year": nc_year})
