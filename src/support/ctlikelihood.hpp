/***************************************************************************
 *              ctlikelihood - Base class for likelihood tools             *
 * ----------------------------------------------------------------------- *
 *  copyright (C) 2016 by Juergen Knoedlseder                              *
 * ----------------------------------------------------------------------- *
 *                                                                         *
 *  This program is free software: you can redistribute it and/or modify   *
 *  it under the terms of the GNU General Public License as published by   *
 *  the Free Software Foundation, either version 3 of the License, or      *
 *  (at your option) any later version.                                    *
 *                                                                         *
 *  This program is distributed in the hope that it will be useful,        *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of         *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
 *  GNU General Public License for more details.                           *
 *                                                                         *
 *  You should have received a copy of the GNU General Public License      *
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.  *
 *                                                                         *
 ***************************************************************************/
/**
 * @file ctlikelihood.hpp
 * @brief Likelihood tool base class interface definition
 * @author Juergen Knoedlseder
 */

#ifndef CTLIKELIHOOD_HPP
#define CTLIKELIHOOD_HPP

/* __ Includes ___________________________________________________________ */
#include "ctool.hpp"

/* __Definitions _________________________________________________________ */


/***********************************************************************//**
 * @class ctlikelihood
 *
 * @brief Base class for likelihood tools
 ***************************************************************************/
class ctlikelihood : public ctool {

public:
    // Constructors and destructors
    ctlikelihood(void);
    ctlikelihood(const std::string& name, const std::string& version);
    ctlikelihood(const std::string& name, const std::string& version,
                 const GObservations& obs);
    ctlikelihood(const std::string& name, const std::string& version,
                 int argc, char* argv[]);
    ctlikelihood(const ctlikelihood& app);
    virtual ~ctlikelihood(void);

    // Operators
    ctlikelihood& operator=(const ctlikelihood& app);

    // Pure virtual methods
    virtual void clear(void) = 0;
    virtual void run(void) = 0;
    virtual void save(void) = 0;

    // Methods
    const GObservations& obs(void) const;
    const GOptimizer*    opt(void) const;

protected:
    // Protected methods
    void   init_members(void);
    void   copy_members(const ctlikelihood& app);
    void   free_members(void);
    double evaluate(GModelPar& par, const double& value);

    // Protected members
    GObservations m_obs; //!< Observation container
    GOptimizerLM  m_opt; //!< Optimizer
};


/***********************************************************************//**
 * @brief Return observation container
 *
 * @return Reference to observation container.
 *
 * Returns a reference to the observation container.
 ***************************************************************************/
inline
const GObservations& ctlikelihood::obs(void) const
{
    return m_obs;
}


/***********************************************************************//**
 * @brief Return optimizer
 *
 * @return Pointer to optimizer.
 *
 * Returns a pointer to the optimizer.
 ***************************************************************************/
inline
const GOptimizer* ctlikelihood::opt(void) const
{
    return &m_opt;
}

#endif /* CTLIKELIHOOD_HPP */
